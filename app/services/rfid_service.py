from app.db.base import SessionLocal
from app.db.models import Student, Book


def get_user_from_uid(uid):
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == uid).first()

        if not student:
            student = db.query(Student).filter(Student.rfid_uid == uid).first()

        if not student:
            student = db.query(Student).filter(Student.koha_id == uid).first()

        if not student:
            return None

        return {
            "name": student.name,
            "koha_id": student.koha_id,
            "roll_number": student.roll_number,
        }

    finally:
        db.close()


def get_book_from_tag(tag):
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.rfid_tag == tag).first()

        if not book:
            return None

        return {
            "id": book.id,
            "title": book.title
        }

    finally:
        db.close()
