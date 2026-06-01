class Session:
    def __init__(self, session_id, user=None):
        self.session_id = session_id
        self.user = user
        self.books = []