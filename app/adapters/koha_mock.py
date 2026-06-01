class KohaMockAdapter:
    def issue_books(self, user_id, book_ids):
        print(f"Issuing {book_ids} to {user_id}")
    
    def return_books(self, book_ids):
        print(f"Returning {book_ids}")
