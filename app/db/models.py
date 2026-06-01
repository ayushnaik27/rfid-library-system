from sqlalchemy import Column, DateTime, String, JSON
from datetime import datetime
from app.db.base import Base


class SessionDB(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    user = Column(JSON)
    books = Column(JSON)


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    koha_id = Column(String)
    rfid_uid = Column(String, unique=True)
    roll_number = Column(String)


class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    rfid_tag = Column(String, unique=True)
   

class RFIDUserMapping(Base):
    __tablename__ = "rfid_user_mappings"

    id = Column(String, primary_key=True, index=True)
    rfid_uid = Column(String, unique=True, index=True)
    user_uid = Column(String, index=True)


class RFIDMapping(Base):
    __tablename__ = "rfid_mappings"

    uid = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    user = Column(JSON)
    books = Column(JSON)
    type = Column(String)  # issue / return
