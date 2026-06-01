from pydantic import BaseModel
from typing import List, Dict, Any


class UserResponse(BaseModel):
    name: str
    koha_id: str


class BookResponse(BaseModel):
    title: str
    id: str


class SessionResponse(BaseModel):
    session_id: str
    user: UserResponse
    books: List[BookResponse] = []