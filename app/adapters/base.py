class LibraryAdapter:
    def issue_books(self, user_id, book_ids):
        raise NotImplementedError

    def return_books(self, book_ids):
        raise NotImplementedError
