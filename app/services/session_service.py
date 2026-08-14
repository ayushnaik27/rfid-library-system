import uuid

from sqlalchemy import text

from app.db.base import SessionLocal
from app.db.models import SessionDB, Transaction
from app.services.rfid_service import get_book_from_tag, get_user_from_uid
from app.utils.logger import logger


class SessionServiceError(Exception):
    status_code = 400
    message = "Session service error"

    def __init__(self, message=None):
        super().__init__(message or self.message)


class EmptyScanError(SessionServiceError):
    message = "No books scanned"


class InvalidBookTagsError(SessionServiceError):
    message = "One or more scanned books were not found"

    def __init__(self, tags):
        self.tags = tags
        super().__init__(self.message)


def _unique_tags(tags):
    seen = set()
    unique = []

    for tag in tags or []:
        clean_tag = str(tag).strip()

        if clean_tag and clean_tag not in seen:
            seen.add(clean_tag)
            unique.append(clean_tag)

    return unique


def _resolve_books_from_tags(tags):
    books_by_id = {}
    invalid_tags = []

    for tag in _unique_tags(tags):
        book = get_book_from_tag(tag)

        if not book:
            invalid_tags.append(tag)
            continue

        books_by_id[book["id"]] = book

    return list(books_by_id.values()), invalid_tags


def _apply_transaction(active_books, transaction):
    for book in transaction.books or []:
        book_id = book.get("id")

        if not book_id:
            continue

        if transaction.type == "issue":
            active_books[book_id] = book
        elif transaction.type == "return":
            active_books.pop(book_id, None)


def _delete_user_sessions(db, user_koha_id):
    sessions = db.query(SessionDB).all()

    for session in sessions:
        user = session.user or {}

        if user.get("koha_id") == user_koha_id:
            db.delete(session)


def end_session(session_id):
    db = SessionLocal()
    try:
        session = db.query(SessionDB).filter(SessionDB.id == session_id).first()

        if not session:
            return False

        db.delete(session)
        db.commit()
        logger.info(f"Session ended: {session_id}")

        return True

    finally:
        db.close()


def get_current_books(user_koha_id):
    db = SessionLocal()
    try:
        transactions = (
            db.query(Transaction)
            .order_by(text("rowid"))
            .all()
        )

        active_books = {}

        for transaction in transactions:
            transaction_user = transaction.user or {}

            if transaction.type == "issue":
                if transaction_user.get("koha_id") != user_koha_id:
                    continue

                _apply_transaction(active_books, transaction)
                continue

            if transaction.type == "return":
                _apply_transaction(active_books, transaction)

        return list(active_books.values())

    finally:
        db.close()


def start_session_for_user(user):
    db = SessionLocal()
    try:
        if not user:
            return None

        session_id = str(uuid.uuid4())
        _delete_user_sessions(db, user["koha_id"])

        session_db = SessionDB(
            id=session_id,
            user=user,
            books=[]
        )

        db.add(session_db)
        db.commit()

        result = {
            "id": session_db.id,
            "user": session_db.user,
            "books": session_db.books
        }

        logger.info(f"Session started: {session_id} for user {user['name']}")

        return result

    finally:
        db.close()


def start_session(user_uid):
    user = get_user_from_uid(user_uid)

    if not user:
        logger.warning(f"User not found for UID: {user_uid}")
        return None

    return start_session_for_user(user)


def add_books(session_id, tags):
    db = SessionLocal()
    try:
        session = db.query(SessionDB).filter(SessionDB.id == session_id).first()

        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None

        books, invalid_tags = _resolve_books_from_tags(tags)

        if invalid_tags:
            logger.warning(f"Invalid book tags for session {session_id}: {invalid_tags}")
            raise InvalidBookTagsError(invalid_tags)

        if not books:
            raise EmptyScanError()

        existing_books = {book["id"]: book for book in session.books or []}

        for book in books:
            existing_books[book["id"]] = book

        session.books = list(existing_books.values())
        db.commit()

        result = {
            "id": session.id,
            "user": session.user,
            "books": session.books
        }

        logger.info(
            f"Books added to session {session_id}: "
            f"{[book['title'] for book in result['books']]}"
        )

        return result

    finally:
        db.close()


def confirm_session(session_id, adapter):
    db = SessionLocal()

    try:
        # -----------------------------------------------------
        # FIND SESSION
        # -----------------------------------------------------

        session = (
            db.query(SessionDB)
            .filter(SessionDB.id == session_id)
            .first()
        )

        if not session:
            logger.warning(
                f"Session not found: {session_id}"
            )
            return None

        # -----------------------------------------------------
        # COPY SESSION DATA
        # -----------------------------------------------------

        books = list(session.books or [])
        user = dict(session.user or {})

        # -----------------------------------------------------
        # VALIDATE SESSION
        # -----------------------------------------------------

        if not books:
            raise EmptyScanError()

        if not user.get("koha_id"):
            raise SessionServiceError(
                "User does not have a KOHA ID"
            )

        # -----------------------------------------------------
        # LOCAL BOOK IDS
        # -----------------------------------------------------

        book_ids = [
            book["id"]
            for book in books
            if book.get("id")
        ]

        if len(book_ids) != len(books):
            raise SessionServiceError(
                "One or more books have no local ID"
            )

        logger.info(
            f"[KOHA] Attempting checkout for user "
            f"{user['koha_id']} "
            f"with books {book_ids}"
        )

        # -----------------------------------------------------
        # ISSUE BOOKS THROUGH ADAPTER
        #
        # KohaRestAdapter performs:
        #
        # local book
        #     ↓
        # accession_number
        #     ↓
        # KOHA external_id
        #     ↓
        # KOHA item_id
        #     ↓
        # availability
        #     ↓
        # checkout
        # -----------------------------------------------------

        koha_result = adapter.issue_books(
            user["koha_id"],
            book_ids,
        )

        if not koha_result:
            raise SessionServiceError(
                "KOHA checkout returned no result"
            )

        successful = koha_result.get(
            "successful",
            []
        )

        failed = koha_result.get(
            "failed",
            []
        )

        # -----------------------------------------------------
        # VERIFY COMPLETE CHECKOUT
        # -----------------------------------------------------

        if failed:
            raise SessionServiceError(
                "One or more books failed to checkout in KOHA"
            )

        if len(successful) != len(book_ids):
            raise SessionServiceError(
                "KOHA did not confirm checkout for "
                "all scanned books"
            )

        # -----------------------------------------------------
        # KOHA SUCCESSFUL
        #
        # Only now create the local transaction.
        # -----------------------------------------------------

        transaction = Transaction(
            id=str(uuid.uuid4()),
            user=user,
            books=books,
            type="issue"
        )

        db.add(transaction)

        # -----------------------------------------------------
        # REMOVE ACTIVE SESSION
        # -----------------------------------------------------

        result = {
            "id": session.id,
            "user": user,
            "books": books
        }

        db.delete(session)

        # -----------------------------------------------------
        # COMMIT LOCAL STATE
        # -----------------------------------------------------

        db.commit()

        logger.info(
            f"[KOHA] Issue transaction saved "
            f"for session {session_id}"
        )

        logger.info(
            f"[KOHA] Successfully issued "
            f"{len(successful)} book(s) "
            f"to patron {user['koha_id']}"
        )

        return result

    finally:
        db.close()


def return_books(tags, adapter):
    db = SessionLocal()
    try:
        returned_books, invalid_tags = _resolve_books_from_tags(tags)

        if invalid_tags:
            logger.warning(f"Invalid book tags for return: {invalid_tags}")
            raise InvalidBookTagsError(invalid_tags)

        if not returned_books:
            raise EmptyScanError()

        book_ids = [book["id"] for book in returned_books]

        adapter.return_books(book_ids)

        transaction = Transaction(
            id=str(uuid.uuid4()),
            user=None,
            books=returned_books,
            type="return"
        )

        db.add(transaction)
        db.commit()

        logger.info(f"Books returned by item scan: {book_ids}")

        return {
            "books": returned_books
        }

    finally:
        db.close()
