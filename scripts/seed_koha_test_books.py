import sqlite3


BOOKS = [
    {
        "id": "B008",
        "accession_number": "502326000821",
        "title": "Dracula",
        "author": "Stoker, Bram",
        "rfid_uid": "A1000008",
    },
    {
        "id": "B009",
        "accession_number": "502326000920",
        "title": "Dragon's blood : a fantasy",
        "author": "Yolen, Jane",
        "rfid_uid": "A1000009",
    },
    {
        "id": "B010",
        "accession_number": "502326000915",
        "title": "Dragonwings",
        "author": "Yep, Laurence",
        "rfid_uid": "A1000010",
    },
    {
        "id": "B011",
        "accession_number": "502326000916",
        "title": "Dragonwings",
        "author": "Yep, Laurence",
        "rfid_uid": "A1000011",
    },
]


def main():
    db = sqlite3.connect("library.db")

    try:
        for book in BOOKS:
            db.execute(
                """
                INSERT OR REPLACE INTO books
                (id, accession_number, title, author, rfid_uid)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    book["id"],
                    book["accession_number"],
                    book["title"],
                    book["author"],
                    book["rfid_uid"],
                ),
            )

        db.commit()

        print("[SEED] KOHA test books added successfully")

        for book in BOOKS:
            print(
                f"{book['id']} | "
                f"{book['title']} | "
                f"{book['accession_number']} | "
                f"{book['rfid_uid']}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()