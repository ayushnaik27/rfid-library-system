from app.db.base import SessionLocal
from app.db.models import Transaction

db = SessionLocal()

transactions = db.query(Transaction).all()

for t in transactions:
    print(t.id, t.type, t.user, t.books)

db.close()