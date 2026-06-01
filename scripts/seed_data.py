from app.db.base import SessionLocal
from app.db.models import Student, Book


def seed():
    db = SessionLocal()

    student1 = Student(
        id="S001",
        name="Rahul",
        koha_id="K001",
        rfid_uid="UID123"
    )

    book1 = Book(
        id="B001",
        title="Math",
        rfid_tag="TAG1"
    )

    book2 = Book(
        id="B002",
        title="Physics",
        rfid_tag="TAG2"
    )
    
    book3 = Book(
        id="B003",
        title="Chemistry",
        rfid_tag="TAG3"
    )
    
    book4 = Book(
        id="B004",
        title="Biology",
        rfid_tag="TAG4"
    )
    
    book5 = Book(
        id="B005",
        title="History",
        rfid_tag="TAG5"
    )
    
    book6 = Book(
        id="B006",
        title="Geography",
        rfid_tag="TAG6"
    )

    db.add_all([book3, book4, book5, book6])
    db.commit()
    db.close()


if __name__ == "__main__":
    seed()