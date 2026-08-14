import requests

from app.adapters.base import LibraryAdapter
from app.config import (
    KOHA_BASE_URL,
    KOHA_CLIENT_ID,
    KOHA_CLIENT_SECRET,
    KOHA_TIMEOUT_SECONDS,
)
from app.services.rfid_mapping_service import get_book_by_id


class KohaRestAdapter(LibraryAdapter):

    def __init__(self):
        self.base_url = KOHA_BASE_URL.rstrip("/")
        self.access_token = None

    # =========================================================
    # AUTHENTICATION
    # =========================================================

    def get_access_token(self):

        if not self.base_url:
            raise RuntimeError(
                "KOHA_BASE_URL is not configured"
            )

        if not KOHA_CLIENT_ID:
            raise RuntimeError(
                "KOHA_CLIENT_ID is not configured"
            )

        if not KOHA_CLIENT_SECRET:
            raise RuntimeError(
                "KOHA_CLIENT_SECRET is not configured"
            )

        response = requests.post(
            f"{self.base_url}/api/v1/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": KOHA_CLIENT_ID,
                "client_secret": KOHA_CLIENT_SECRET,
            },
            timeout=KOHA_TIMEOUT_SECONDS,
        )

        if not response.ok:

            print(
                f"[KOHA] OAuth failed: "
                f"HTTP {response.status_code}"
            )

            print(
                f"[KOHA] Response: {response.text}"
            )

            raise RuntimeError(
                "KOHA OAuth authentication failed"
            )

        data = response.json()

        access_token = data.get("access_token")

        if not access_token:
            raise RuntimeError(
                "KOHA OAuth response did not contain "
                "an access token"
            )

        self.access_token = access_token

        return self.access_token

    # =========================================================
    # AUTHENTICATED HEADERS
    # =========================================================

    def _headers(self):

        if not self.access_token:
            self.get_access_token()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    # =========================================================
    # GENERIC KOHA REQUEST
    # =========================================================

    def _request(self, method, url, **kwargs):

        response = requests.request(
            method,
            url,
            headers=self._headers(),
            timeout=KOHA_TIMEOUT_SECONDS,
            **kwargs,
        )

        # -----------------------------------------------------
        # Retry once after token expiration
        # -----------------------------------------------------

        if response.status_code == 401:

            self.access_token = None

            response = requests.request(
                method,
                url,
                headers=self._headers(),
                timeout=KOHA_TIMEOUT_SECONDS,
                **kwargs,
            )

        response.raise_for_status()

        return response

    # =========================================================
    # PATRON LOOKUP
    # =========================================================

    def get_patron(self, koha_id):

        response = self._request(
            "GET",
            f"{self.base_url}/api/v1/patrons",
            params={
                "cardnumber": koha_id,
            },
        )

        patrons = response.json()

        if not patrons:
            raise ValueError(
                f"KOHA patron not found: {koha_id}"
            )

        return patrons[0]

    # =========================================================
    # ITEM LOOKUP
    # =========================================================

    def get_item(self, external_id):

        response = self._request(
            "GET",
            f"{self.base_url}/api/v1/items",
            params={
                "external_id": external_id,
                "_match": "exact",
            },
        )

        items = response.json()

        if not items:
            raise ValueError(
                f"KOHA item not found: {external_id}"
            )

        # -----------------------------------------------------
        # Verify the returned item actually matches
        # -----------------------------------------------------

        matching_items = [
            item
            for item in items
            if item.get("external_id") == external_id
        ]

        if not matching_items:
            raise ValueError(
                f"KOHA returned no exact item match "
                f"for external ID: {external_id}"
            )

        if len(matching_items) > 1:
            raise ValueError(
                f"Multiple KOHA items found for external ID: "
                f"{external_id}"
            )

        return matching_items[0]

    # =========================================================
    # CHECKOUT AVAILABILITY
    # =========================================================

    def checkout_availability(self, patron_id, item_id):

        response = self._request(
            "GET",
            f"{self.base_url}/api/v1/checkouts/availability",
            params={
                "patron_id": patron_id,
                "item_id": item_id,
            },
        )

        return response.json()

    # =========================================================
    # ACTUAL CHECKOUT
    # =========================================================

    def issue_book(self, patron_id, item_id):

        availability = self.checkout_availability(
            patron_id,
            item_id,
        )

        blockers = availability.get(
            "blockers",
            {},
        )

        confirms = availability.get(
            "confirms",
            {},
        )

        warnings = availability.get(
            "warnings",
            {},
        )

        # -----------------------------------------------------
        # Blocked checkout
        # -----------------------------------------------------

        if blockers:

            raise RuntimeError(
                f"KOHA checkout blocked: {blockers}"
            )

        # -----------------------------------------------------
        # Confirmation required
        #
        # For our kiosk's normal ISSUE operation, we do not
        # automatically approve confirmations such as
        # RENEW_ISSUE.
        # -----------------------------------------------------

        if confirms:

            raise RuntimeError(
                f"KOHA checkout requires confirmation: "
                f"{confirms}"
            )

        # -----------------------------------------------------
        # Confirmation token
        # -----------------------------------------------------

        confirmation_token = availability.get(
            "confirmation_token"
        )

        if not confirmation_token:

            raise RuntimeError(
                "KOHA did not provide a confirmation token"
            )

        # -----------------------------------------------------
        # Perform checkout
        # -----------------------------------------------------

        response = self._request(
            "POST",
            f"{self.base_url}/api/v1/checkouts",
            params={
                "confirmation": confirmation_token,
            },
            json={
                "patron_id": patron_id,
                "item_id": item_id,
            },
        )

        return response.json()

    # =========================================================
    # ISSUE MULTIPLE BOOKS
    # =========================================================

    def issue_books(self, user_id, book_ids):

        if not book_ids:
            raise ValueError(
                "No books supplied for checkout"
            )

        # -----------------------------------------------------
        # STEP 1: Resolve patron
        # -----------------------------------------------------

        patron = self.get_patron(user_id)

        patron_id = patron.get(
            "patron_id"
        )

        if not patron_id:

            raise RuntimeError(
                f"KOHA patron ID not found for user: "
                f"{user_id}"
            )

        # -----------------------------------------------------
        # STEP 2: Resolve ALL books first
        # -----------------------------------------------------

        resolved_books = []

        for book_id in book_ids:

            local_book = get_book_by_id(
                book_id
            )

            if not local_book:

                raise ValueError(
                    f"Local book not found: "
                    f"{book_id}"
                )

            # -------------------------------------------------
            # Our design:
            #
            # accession_number = KOHA external_id
            # -------------------------------------------------

            external_id = local_book.get(
                "accession_number"
            )

            if not external_id:

                raise ValueError(
                    f"Book {book_id} has no "
                    f"accession number"
                )

            koha_item = self.get_item(
                external_id
            )

            item_id = koha_item.get(
                "item_id"
            )

            if not item_id:

                raise RuntimeError(
                    f"KOHA item ID not found for "
                    f"external ID: {external_id}"
                )

            resolved_books.append(
                {
                    "local_book_id": book_id,
                    "external_id": external_id,
                    "koha_item_id": item_id,
                    "local_book": local_book,
                    "koha_item": koha_item,
                }
            )

        # -----------------------------------------------------
        # STEP 3: Check availability for ALL books
        # -----------------------------------------------------

        availability_results = []

        for book in resolved_books:

            availability = self.checkout_availability(
                patron_id,
                book["koha_item_id"],
            )

            blockers = availability.get(
                "blockers",
                {},
            )

            confirms = availability.get(
                "confirms",
                {},
            )

            warnings = availability.get(
                "warnings",
                {},
            )

            availability_results.append(
                {
                    "local_book_id": book[
                        "local_book_id"
                    ],
                    "external_id": book[
                        "external_id"
                    ],
                    "koha_item_id": book[
                        "koha_item_id"
                    ],
                    "availability": availability,
                    "blockers": blockers,
                    "confirms": confirms,
                    "warnings": warnings,
                }
            )

        # -----------------------------------------------------
        # STEP 4: Find books that cannot be issued
        #
        # We reject BOTH blockers and confirmations.
        # -----------------------------------------------------

        unavailable_books = [
            result
            for result in availability_results
            if (
                result["blockers"]
                or result["confirms"]
            )
        ]

        # -----------------------------------------------------
        # STEP 5: Abort BEFORE issuing anything
        # -----------------------------------------------------

        if unavailable_books:

            raise RuntimeError(
                {
                    "message": (
                        "One or more books "
                        "cannot be issued"
                    ),
                    "unavailable_books": (
                        unavailable_books
                    ),
                }
            )

        # -----------------------------------------------------
        # STEP 6: Make sure every book has a token
        # -----------------------------------------------------

        for result in availability_results:

            confirmation_token = (
                result["availability"].get(
                    "confirmation_token"
                )
            )

            if not confirmation_token:

                raise RuntimeError(
                    "KOHA did not provide a "
                    "confirmation token for "
                    f"item "
                    f"{result['koha_item_id']}"
                )

        # -----------------------------------------------------
        # STEP 7: All books passed validation.
        # Now perform actual checkouts.
        # -----------------------------------------------------

        successful = []

        for book in resolved_books:

            checkout = self.issue_book(
                patron_id,
                book["koha_item_id"],
            )

            successful.append(
                {
                    "local_book_id": (
                        book["local_book_id"]
                    ),
                    "koha_item_id": (
                        book["koha_item_id"]
                    ),
                    "checkout": checkout,
                }
            )

        # -----------------------------------------------------
        # STEP 8: Return structured result
        # -----------------------------------------------------

        return {
            "patron_id": patron_id,
            "successful": successful,
            "failed": [],
        }

    # =========================================================
    # RETURN BOOKS
    # =========================================================

    def return_books(self, book_ids):

        raise NotImplementedError(
            "KOHA return integration is not implemented yet"
        )