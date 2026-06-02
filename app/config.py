import os
from pathlib import Path


def _load_dotenv():
    env_path = Path(__file__).resolve().parents[1] / ".env"

    if not env_path.exists():
        print("[CONFIG] .env file not found, using defaults")
        return

    print(f"[CONFIG] Loading environment from: {env_path}")

    for line in env_path.read_text().splitlines():
        clean_line = line.strip()

        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        key, value = clean_line.split("=", 1)

        os.environ.setdefault(
            key.strip(),
            value.strip().strip('"').strip("'")
        )


# Load environment variables
_load_dotenv()


# =========================================================
# RFID MODE CONFIGURATION
# =========================================================

RFID_MODE = os.getenv(
    "RFID_MODE",
    os.getenv("SCANNER_MODE", "hardware")
).lower()

SCANNER_MODE = RFID_MODE

print(f"[CONFIG] RFID_MODE = {RFID_MODE}")


# =========================================================
# RFID SERIAL CONFIGURATION
# =========================================================

RFID_SERIAL_PORTS = [
    port.strip()
    for port in os.getenv(
        "RFID_SERIAL_PORTS",
        "COM3"
    ).split(",")
    if port.strip()
]

print(f"[CONFIG] RFID_SERIAL_PORTS = {RFID_SERIAL_PORTS}")

RFID_BAUD_RATE = int(
    os.getenv(
        "RFID_BAUD_RATE",
        "115200"
    )
)

print(f"[CONFIG] RFID_BAUD_RATE = {RFID_BAUD_RATE}")

RFID_READ_TIMEOUT_SECONDS = float(
    os.getenv(
        "RFID_READ_TIMEOUT_SECONDS",
        "1"
    )
)

RFID_RECONNECT_DELAY_SECONDS = float(
    os.getenv(
        "RFID_RECONNECT_DELAY_SECONDS",
        "2"
    )
)

RFID_POLL_INTERVAL_SECONDS = float(
    os.getenv(
        "RFID_POLL_INTERVAL_SECONDS",
        "0.1"
    )
)

RFID_DUPLICATE_WINDOW_SECONDS = float(
    os.getenv(
        "RFID_DUPLICATE_WINDOW_SECONDS",
        "1.5"
    )
)

RFID_VALID_UID_PATTERN = os.getenv(
    "RFID_VALID_UID_PATTERN",
    r"^[0-9A-F]{8,32}$"
)


# =========================================================
# MOCK RFID CONFIGURATION
# =========================================================

MOCK_RFID_TAGS = [
    tag.strip()
    for tag in os.getenv(
        "MOCK_RFID_TAGS",
        "TAG1,TAG2,TAG3,TAG4,TAG5,TAG_UNKNOWN"
    ).split(",")
    if tag.strip()
]

MOCK_READER_AUTO_SCAN = (
    os.getenv(
        "MOCK_READER_AUTO_SCAN",
        "false"
    ).lower() == "true"
)


# =========================================================
# DEFAULT RFID USER MAPPINGS
# =========================================================

DEFAULT_RFID_MAPPINGS = [
    {
        "uid": "17625E05",
        "user_id": "K001",
        "user_name": "Ayush",
        "roll_number": "22124023",
    }
]


# =========================================================
# DEBUG STARTUP LOGS
# =========================================================

print("[CONFIG] Configuration loaded successfully")

if RFID_MODE == "hardware":
    print("[RFID] Hardware mode enabled")
    print(f"[RFID] Will attempt ports: {RFID_SERIAL_PORTS}")
    print(f"[RFID] Baud rate: {RFID_BAUD_RATE}")

else:
    print("[RFID] Mock mode enabled")