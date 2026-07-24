import logging

from app.db.base import SessionLocal
from app.db.models import Student, Book

logger = logging.getLogger(__name__)


# =========================================================
# NORMALIZE RFID UID
# =========================================================

def normalize_rfid_uid(uid):

    if uid is None:
        return ""

    return str(uid).strip().upper()


# =========================================================
# STUDENT SERIALIZER
# =========================================================

def student_to_dict(student):

    if not student:
        return None

    return {
        "id": student.id,
        "name": student.name,
        "koha_id": student.koha_id,
        "roll_number": student.roll_number,
        "rfid_uid": student.rfid_uid,
    }


# =========================================================
# BOOK SERIALIZER
# =========================================================

def book_to_dict(book):

    if not book:
        return None

    return {
        "id": book.id,
        "accession_number": book.accession_number,
        "title": book.title,
        "author": book.author,
        "rfid_uid": book.rfid_uid,
    }


# =========================================================
# FIND STUDENT BY RFID UID
# =========================================================

def map_uid_to_user(rfid_uid):

    db = SessionLocal()

    try:

        clean_uid = normalize_rfid_uid(rfid_uid)

        if not clean_uid:
            return None

        student = (
            db.query(Student)
            .filter(Student.rfid_uid == clean_uid)
            .first()
        )

        if student:

            logger.info(
                "[RFID] Student resolved: %s",
                student.roll_number
            )

        return student_to_dict(student)

    finally:
        db.close()


# =========================================================
# FIND BOOK BY RFID UID
# =========================================================

def map_uid_to_book(rfid_uid):

    db = SessionLocal()

    try:

        clean_uid = normalize_rfid_uid(rfid_uid)

        if not clean_uid:
            return None

        book = (
            db.query(Book)
            .filter(Book.rfid_uid == clean_uid)
            .first()
        )

        if book:

            logger.info(
                "[RFID] Book resolved: %s",
                book.accession_number
            )

        return book_to_dict(book)

    finally:
        db.close()


# =========================================================
# GET USER BY USER ID
# =========================================================

def get_user_by_uid(user_id):

    db = SessionLocal()

    try:

        student = (
            db.query(Student)
            .filter(Student.id == user_id)
            .first()
        )

        return student_to_dict(student)

    finally:
        db.close()


# =========================================================
# GET BOOK BY BOOK ID
# =========================================================

def get_book_by_id(book_id):

    db = SessionLocal()

    try:

        book = (
            db.query(Book)
            .filter(Book.id == book_id)
            .first()
        )

        return book_to_dict(book)

    finally:
        db.close()