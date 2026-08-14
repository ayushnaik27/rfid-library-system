from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.adapters.koha_mock import KohaMockAdapter
from app.adapters.koha_rest import KohaRestAdapter
from app.schemas.session_schema import SessionResponse
from app.services.rfid_mapping_service import map_uid_to_user
from app.services.rfid_service import get_book_from_tag
from app.services.scan_service import scan_service
from app.services.session_service import (
    EmptyScanError,
    InvalidBookTagsError,
    add_books,
    confirm_session,
    end_session,
    get_current_books,
    return_books,
    start_session_for_user,
    start_session,
)
from app.utils.response import success_response

router = APIRouter()
adapter = KohaRestAdapter()
logger = logging.getLogger(__name__)


class StartRequest(BaseModel):
    user_uid: str


class BooksRequest(BaseModel):
    session_id: str
    tags: list[str]


class ConfirmRequest(BaseModel):
    session_id: str


class ReturnRequest(BaseModel):
    tags: list[str]


class RFIDLoginRequest(BaseModel):
    uid: str


def _service_error_response(error):
    detail = {"message": error.message}

    if isinstance(error, InvalidBookTagsError):
        detail["invalid_tags"] = error.tags

    raise HTTPException(status_code=400, detail=detail)


@router.post("/start")
def start(data: StartRequest):
    session = start_session(data.user_uid)

    if not session:
        raise HTTPException(
            status_code=404,
            detail={"message": "User not found"}
        )

    return success_response(
        data=SessionResponse(
            session_id=session["id"],
            user=session["user"],
            books=session["books"]
        ),
        message="Session started"
    )


@router.post("/rfid/login")
def rfid_login(data: RFIDLoginRequest):
    logger.info("[RFID] Login requested for UID: %s", data.uid)
    user = map_uid_to_user(data.uid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail={"message": "RFID card not registered"}
        )

    session = start_session_for_user(user)

    if not session:
        raise HTTPException(
            status_code=500,
            detail={"message": "Could not start session"}
        )

    logger.info("[SESSION] Session created via RFID for user: %s", user["koha_id"])

    return success_response(
        data=SessionResponse(
            session_id=session["id"],
            user=session["user"],
            books=session["books"]
        ),
        message="RFID login successful"
    )


@router.post("/api/rfid/login")
def api_rfid_login(data: RFIDLoginRequest):
    return rfid_login(data)


@router.post("/books")
def books(data: BooksRequest):
    try:
        session = add_books(data.session_id, data.tags)
    except (EmptyScanError, InvalidBookTagsError) as error:
        _service_error_response(error)

    if not session:
        raise HTTPException(
            status_code=404,
            detail={"message": "Invalid session"}
        )

    return success_response(
        data=SessionResponse(
            session_id=session["id"],
            user=session["user"],
            books=session["books"]
        ),
        message="Books added to session"
    )


@router.get("/book/{tag}")
def get_book(tag: str):
    book = get_book_from_tag(tag)

    if not book:
        raise HTTPException(
            status_code=404,
            detail={"message": "Book not found"}
        )

    return book


@router.get("/users/{koha_id}/current-books")
def current_books(koha_id: str):
    books = get_current_books(koha_id)

    return success_response(
        data={
            "koha_id": koha_id,
            "count": len(books),
            "books": books
        },
        message="Current issued books fetched"
    )


@router.get("/scanner/latest")
def latest_scan():
    scan = scan_service.get_latest_scan()

    if not scan:
        return success_response(data=None, message="No scan available")

    return success_response(
        data={"uid": scan["uid"]},
        message="Latest scan fetched"
    )


@router.get("/api/rfid/latest")
def latest_rfid_scan():
    scan = scan_service.get_latest_scan()

    if not scan:
        return {
            "uid": None,
            "timestamp": None,
        }

    return {
        "uid": scan["uid"],
        "timestamp": scan.get("timestamp"),
    }


@router.delete("/sessions/{session_id}")
def close_session(session_id: str):
    ended = end_session(session_id)

    if not ended:
        raise HTTPException(
            status_code=404,
            detail={"message": "Invalid session"}
        )

    return success_response(message="Session ended")


@router.post("/confirm")
def confirm(data: ConfirmRequest):
    try:
        session = confirm_session(data.session_id, adapter)
    except EmptyScanError as error:
        _service_error_response(error)

    if not session:
        raise HTTPException(
            status_code=404,
            detail={"message": "Invalid session"}
        )

    return success_response(
        data=SessionResponse(
            session_id=session["id"],
            user=session["user"],
            books=session["books"]
        ),
        message="Session confirmed"
    )


@router.post("/return")
def return_books_api(data: ReturnRequest):
    try:
        result = return_books(data.tags, adapter)
    except (EmptyScanError, InvalidBookTagsError) as error:
        _service_error_response(error)

    if not result:
        raise HTTPException(
            status_code=404,
            detail={"message": "Books not found"}
        )

    return success_response(
        data={
            "books": result["books"]
        },
        message="Books returned successfully"
    )
