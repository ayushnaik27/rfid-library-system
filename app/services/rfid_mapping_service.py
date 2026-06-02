from datetime import datetime
import logging

from app.config import DEFAULT_RFID_MAPPINGS
from app.db.base import SessionLocal
from app.db.models import RFIDMapping, Student

logger = logging.getLogger(__name__)


def normalize_rfid_uid(uid):
    if uid is None:
        return ""

    return str(uid).strip().upper()


def _student_to_user(student):
    if not student:
        return None

    return {
        "name": student.name,
        "koha_id": student.koha_id,
        "roll_number": student.roll_number,
    }


def _ensure_student_for_mapping(db, mapping):
    if not mapping:
        return None

    student = db.query(Student).filter(Student.id == mapping.user_id).first()

    if not student:
        student = Student(
            id=mapping.user_id,
            name=mapping.user_name or mapping.user_id,
            koha_id=mapping.user_id,
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        logger.info("[DB] Created missing user row for RFID mapping: %s", mapping.user_id)
    else:
        changed = False

        if not student.koha_id:
            student.koha_id = mapping.user_id
            changed = True

        if mapping.user_name and student.name != mapping.user_name:
            student.name = mapping.user_name
            changed = True

        if changed:
            db.commit()
            db.refresh(student)

    return student


def _mapping_to_user(db, mapping):
    if not mapping:
        return None

    student = _ensure_student_for_mapping(db, mapping)
    user = _student_to_user(student)

    if user:
        return user

    logger.warning("[RFID] Mapping found but user could not be resolved: %s", mapping.user_id)
    return None


def map_uid_to_user(rfid_uid):
    db = SessionLocal()
    try:
        clean_uid = normalize_rfid_uid(rfid_uid)

        if not clean_uid:
            return None

        mapping = db.query(RFIDMapping).filter(RFIDMapping.uid == clean_uid).first()
        user = _mapping_to_user(db, mapping)

        if user:
            logger.info("[RFID] User resolved: %s", user["koha_id"])

        return user

    finally:
        db.close()


def get_user_by_uid(user_uid):
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == user_uid).first()
        user = _student_to_user(student)

        if user:
            return user

        mapping = db.query(RFIDMapping).filter(RFIDMapping.user_id == user_uid).first()
        return _mapping_to_user(db, mapping)

    finally:
        db.close()


def create_mapping(rfid_uid, user_id, user_name=None):
    db = SessionLocal()
    try:
        clean_uid = normalize_rfid_uid(rfid_uid)

        if not clean_uid or not user_id:
            return None

        mapping = db.query(RFIDMapping).filter(RFIDMapping.uid == clean_uid).first()

        if not mapping:
            mapping = RFIDMapping(
                uid=clean_uid,
                user_id=user_id,
                user_name=user_name or user_id,
                created_at=datetime.utcnow(),
            )
            db.add(mapping)
        else:
            mapping.user_id = user_id
            mapping.user_name = user_name or mapping.user_name or user_id

        student = db.query(Student).filter(Student.id == user_id).first()

        if not student:
            db.add(Student(
                id=user_id,
                name=user_name or user_id,
                koha_id=user_id,
            ))
        else:
            student.name = user_name or student.name
            student.koha_id = student.koha_id or user_id

        db.commit()

        return {
            "uid": mapping.uid,
            "user_id": mapping.user_id,
            "user_name": mapping.user_name,
            "created_at": mapping.created_at.isoformat() if mapping.created_at else None,
        }

    finally:
        db.close()


def ensure_default_mappings():
    for mapping in DEFAULT_RFID_MAPPINGS:
        create_mapping(
            mapping["uid"],
            mapping["user_id"],
            mapping["user_name"],
        )
