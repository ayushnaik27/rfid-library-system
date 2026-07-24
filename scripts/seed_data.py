from app.db.base import SessionLocal
from app.db.models import Student


def add_student():

    db = SessionLocal()

    try:

        # Check if RFID already exists
        existing_student = (
            db.query(Student)
            .filter(Student.rfid_uid == "07375605")
            .first()
        )

        if existing_student:
            print("RFID already assigned to:")
            print(existing_student.name)
            return

        # Create new student
        student = Student(
            id="K002",
            name="New Student",
            koha_id="K002",
            roll_number="22124024",
            rfid_uid="07375605"
        )

        db.add(student)

        db.commit()

        print("Student added successfully!")

    except Exception as e:

        db.rollback()

        print("Error:", e)

    finally:

        db.close()


if __name__ == "__main__":
    add_student()