import logging

from sqlalchemy import inspect, text

from app.db.base import SessionLocal, engine
from app.db.models import Student, Book

logger = logging.getLogger(__name__)


# =========================================================
# ENSURE SQLITE SCHEMA
# =========================================================

def ensure_sqlite_schema():

    inspector = inspect(engine)

    # -----------------------------------------------------
    # STUDENTS TABLE
    # -----------------------------------------------------

    if "students" in inspector.get_table_names():

        student_columns = {
            column["name"]
            for column in inspector.get_columns("students")
        }

        if "roll_number" not in student_columns:

            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE students "
                        "ADD COLUMN roll_number VARCHAR"
                    )
                )

            logger.info(
                "[DB] Added students.roll_number"
            )

        if "rfid_uid" not in student_columns:

            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE students "
                        "ADD COLUMN rfid_uid VARCHAR"
                    )
                )

            logger.info(
                "[DB] Added students.rfid_uid"
            )

    # -----------------------------------------------------
    # BOOKS TABLE
    # -----------------------------------------------------

    if "books" in inspector.get_table_names():

        book_columns = {
            column["name"]
            for column in inspector.get_columns("books")
        }

        if "accession_number" not in book_columns:

            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE books "
                        "ADD COLUMN accession_number VARCHAR"
                    )
                )

            logger.info(
                "[DB] Added books.accession_number"
            )

        if "author" not in book_columns:

            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE books "
                        "ADD COLUMN author VARCHAR"
                    )
                )

            logger.info(
                "[DB] Added books.author"
            )

        if "rfid_uid" not in book_columns:

            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE books "
                        "ADD COLUMN rfid_uid VARCHAR"
                    )
                )

            logger.info(
                "[DB] Added books.rfid_uid"
            )


# =========================================================
# CREATE DEFAULT STUDENTS
# =========================================================

def ensure_default_students():

    db = SessionLocal()

    try:

        student = (
            db.query(Student)
            .filter(Student.id == "K001")
            .first()
        )

        if not student:

            student = Student(
                id="K001",
                name="Ayush",
                koha_id="K001",
                roll_number="22124023",
                rfid_uid="17625E05"
            )

            db.add(student)

            logger.info(
                "[DB] Default student created"
            )

        else:

            student.name = "Ayush"

            student.roll_number = "22124023"

            student.koha_id = "K001"

            student.rfid_uid = "17625E05"

            logger.info(
                "[DB] Default student updated"
            )

        db.commit()

    finally:
        db.close()


# =========================================================
# CREATE DEFAULT BOOKS
# =========================================================

def ensure_default_books():

    db = SessionLocal()

    try:

        demo_books = [

            {
                "id": "B001",
                "accession_number": "ACC001",
                "title": "Operating Systems",
                "author": "Galvin",
                "rfid_uid": "974C5B05"
            },

            {
                "id": "B002",
                "accession_number": "ACC002",
                "title": "Database Management Systems",
                "author": "Korth",
                "rfid_uid": "474F5705"
            },

            {
                "id": "B003",
                "accession_number": "ACC003",
                "title": "Computer Networks",
                "author": "Tanenbaum",
                "rfid_uid": "C7535B05"
            }

        ]

        for book_data in demo_books:

            existing_book = (
                db.query(Book)
                .filter(Book.id == book_data["id"])
                .first()
            )

            if not existing_book:

                book = Book(
                    id=book_data["id"],
                    accession_number=book_data["accession_number"],
                    title=book_data["title"],
                    author=book_data["author"],
                    rfid_uid=book_data["rfid_uid"]
                )

                db.add(book)

                logger.info(
                    "[DB] Added book: %s",
                    book.title
                )

        db.commit()

    finally:
        db.close()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database_state():

    ensure_sqlite_schema()

    ensure_default_students()

    ensure_default_books()