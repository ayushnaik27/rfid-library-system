from app.db.base import SessionLocal
from app.db.models import Student, Book


# =========================================================
# GET USER FROM RFID UID
# =========================================================

def get_user_from_uid(uid):

    db = SessionLocal()

    try:

        clean_uid = str(uid).strip().upper()

        # -------------------------------------------------
        # SEARCH BY RFID UID
        # -------------------------------------------------

        student = (
            db.query(Student)
            .filter(Student.rfid_uid == clean_uid)
            .first()
        )

        # -------------------------------------------------
        # FALLBACK SEARCHES
        # -------------------------------------------------

        if not student:

            student = (
                db.query(Student)
                .filter(Student.id == clean_uid)
                .first()
            )

        if not student:

            student = (
                db.query(Student)
                .filter(Student.koha_id == clean_uid)
                .first()
            )

        if not student:
            return None

        return {
            "id": student.id,
            "name": student.name,
            "koha_id": student.koha_id,
            "roll_number": student.roll_number,
            "rfid_uid": student.rfid_uid,
        }

    finally:
        db.close()


# =========================================================
# GET BOOK FROM RFID UID
# =========================================================

def get_book_from_tag(tag):

    db = SessionLocal()

    try:

        clean_tag = str(tag).strip().upper()

        # -------------------------------------------------
        # SEARCH BOOK RFID
        # -------------------------------------------------

        book = (
            db.query(Book)
            .filter(Book.rfid_uid == clean_tag)
            .first()
        )

        # -------------------------------------------------
        # OPTIONAL FALLBACK SEARCH
        # -------------------------------------------------

        if not book:

            book = (
                db.query(Book)
                .filter(Book.accession_number == clean_tag)
                .first()
            )

        if not book:
            return None

        return {
            "id": book.id,
            "accession_number": book.accession_number,
            "title": book.title,
            "author": book.author,
            "rfid_uid": book.rfid_uid,
        }

    finally:
        db.close()