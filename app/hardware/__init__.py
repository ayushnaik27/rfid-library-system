from app.config import (
    MOCK_RFID_TAGS,
    MOCK_READER_AUTO_SCAN,
    RFID_BAUD_RATE,
    RFID_READ_TIMEOUT_SECONDS,
    RFID_RECONNECT_DELAY_SECONDS,
    RFID_SERIAL_PORTS,
    RFID_MODE,
)
from app.hardware.base_reader import RFIDReader
from app.hardware.mock_reader import MockRFIDReader
from app.hardware.rfid_reader import ESP32SerialRFIDReader


def create_rfid_reader() -> RFIDReader:
    if RFID_MODE == "hardware":
        return ESP32SerialRFIDReader(
            ports=RFID_SERIAL_PORTS,
            baud_rate=RFID_BAUD_RATE,
            timeout=RFID_READ_TIMEOUT_SECONDS,
            reconnect_delay=RFID_RECONNECT_DELAY_SECONDS,
        )

    return MockRFIDReader(
        tags=MOCK_RFID_TAGS if MOCK_READER_AUTO_SCAN else [],
        delay_seconds=RFID_READ_TIMEOUT_SECONDS,
    )
