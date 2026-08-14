from app.adapters.koha_rest import KohaRestAdapter
from app.services.rfid_mapping_service import map_uid_to_user
from app.services.session_service import (
    add_books,
    confirm_session,
    start_session_for_user,
)


def main():

    print("[TEST] Starting confirm_session integration test")

    # ---------------------------------------------------------
    # Resolve test patron from RFID UID
    # ---------------------------------------------------------

    user = map_uid_to_user("17625E05")

    if not user:
        raise RuntimeError(
            "Test patron not found"
        )

    print(
        f"[TEST] User: "
        f"{user['name']} "
        f"(KOHA ID: {user['koha_id']})"
    )

    # ---------------------------------------------------------
    # Create session
    # ---------------------------------------------------------

    session = start_session_for_user(user)

    if not session:
        raise RuntimeError(
            "Could not create test session"
        )

    print(
        f"[TEST] Session created: "
        f"{session['id']}"
    )

    # ---------------------------------------------------------
    # Add book using RFID UID
    # ---------------------------------------------------------

    session = add_books(
        session["id"],
        ["A1000008"],
    )

    if not session:
        raise RuntimeError(
            "Could not add book to session"
        )

    print("[TEST] Book added to session")

    for book in session["books"]:
        print(
            f"  {book['id']} | "
            f"{book['title']} | "
            f"{book['accession_number']}"
        )

    # ---------------------------------------------------------
    # Confirm through REAL KOHA adapter
    # ---------------------------------------------------------

    adapter = KohaRestAdapter()

    result = confirm_session(
        session["id"],
        adapter,
    )

    if not result:
        raise RuntimeError(
            "confirm_session returned no result"
        )

    # ---------------------------------------------------------
    # Success
    # ---------------------------------------------------------

    print()
    print("[TEST] confirm_session SUCCESS")

    print(
        f"User: "
        f"{result['user']['name']}"
    )

    print(
        f"Books confirmed: "
        f"{len(result['books'])}"
    )

    for book in result["books"]:
        print(
            f"  Local ID: "
            f"{book['id']}"
        )

        print(
            f"  KOHA external ID: "
            f"{book['accession_number']}"
        )

        print(
            f"  Title: "
            f"{book['title']}"
        )


if __name__ == "__main__":
    main()