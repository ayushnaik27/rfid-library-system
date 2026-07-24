from sqlalchemy import Column, DateTime, String, JSON
from datetime import datetime

from app.db.base import Base


# =========================================================
# ACTIVE SESSION STORAGE
# =========================================================

class SessionDB(Base):
    __tablename__ = "sessions"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    user = Column(JSON)

    books = Column(JSON)


# =========================================================
# STUDENT TABLE
# =========================================================

class Student(Base):
    __tablename__ = "students"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    name = Column(String)

    koha_id = Column(String)

    roll_number = Column(String)

    # RFID card assigned to student
    rfid_uid = Column(
        String,
        unique=True,
        index=True
    )


# =========================================================
# BOOK TABLE
# =========================================================

class Book(Base):
    __tablename__ = "books"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    accession_number = Column(
        String,
        unique=True,
        index=True
    )

    title = Column(String)

    author = Column(String)

    # RFID tag attached to book
    rfid_uid = Column(
        String,
        unique=True,
        index=True
    )


# =========================================================
# TRANSACTION HISTORY
# =========================================================

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        String,
        primary_key=True
    )

    user = Column(JSON)

    books = Column(JSON)

    # issue / return
    type = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )