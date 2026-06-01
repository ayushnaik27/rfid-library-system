from fastapi import FastAPI
from app.api.routes import router
from app.utils.exception_handler import http_exception_handler, validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.db_init_service import initialize_database_state
from app.services.scan_service import scan_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def start_scanner():
    initialize_database_state()
    scan_service.start_reader()


@app.on_event("shutdown")
def stop_scanner():
    scan_service.stop_reader()


@app.get("/")
def home():
    return {"message": "RFID Library System Running"}

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Create database tables
from app.db.base import engine, Base

Base.metadata.create_all(bind=engine)
