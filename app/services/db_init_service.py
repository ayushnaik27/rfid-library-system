import logging

from sqlalchemy import inspect, text

from app.config import DEFAULT_RFID_MAPPINGS
from app.db.base import SessionLocal, engine
from app.db.models import Student
from app.services.rfid_mapping_service import create_mapping

logger = logging.getLogger(__name__)


def ensure_sqlite_schema():
    inspector = inspect(engine)

    if "students" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("students")}

    if "roll_number" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE students ADD COLUMN roll_number VARCHAR"))
        logger.info("[DB] Added students.roll_number column")


def ensure_default_users_and_mappings():
    db = SessionLocal()
    try:
        for mapping in DEFAULT_RFID_MAPPINGS:
            user_id = mapping["user_id"]
            user_name = mapping["user_name"]
            roll_number = mapping.get("roll_number")

            student = db.query(Student).filter(Student.id == user_id).first()

            if not student:
                student = Student(
                    id=user_id,
                    name=user_name,
                    koha_id=user_id,
                    roll_number=roll_number,
                )
                db.add(student)
            else:
                student.name = user_name
                student.koha_id = student.koha_id or user_id
                student.roll_number = roll_number or student.roll_number

        db.commit()
    finally:
        db.close()

    for mapping in DEFAULT_RFID_MAPPINGS:
        create_mapping(
            mapping["uid"],
            mapping["user_id"],
            mapping["user_name"],
        )
        logger.info("[RFID] Default mapping ensured: %s -> %s", mapping["uid"], mapping["user_id"])


def initialize_database_state():
    ensure_sqlite_schema()
    ensure_default_users_and_mappings()
