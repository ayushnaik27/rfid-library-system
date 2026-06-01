import logging
import re
import time

from app.config import RFID_VALID_UID_PATTERN
from app.hardware.base_reader import RFIDReader

logger = logging.getLogger(__name__)


class ESP32SerialRFIDReader(RFIDReader):
    def __init__(
        self,
        ports,
        baud_rate=9600,
        timeout=1,
        reconnect_delay=2,
        uid_pattern=RFID_VALID_UID_PATTERN,
        serial_factory=None,
    ):
        self.ports = list(ports or [])
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.reconnect_delay = reconnect_delay
        self.uid_pattern = re.compile(uid_pattern)
        self.serial_factory = serial_factory or self._load_serial_factory()
        self.serial_connection = None
        self.active_port = None
        self.last_connect_attempt = 0

    def _load_serial_factory(self):
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError(
                "pyserial is required for RFID hardware mode. "
                "Install it with: pip install pyserial"
            ) from exc

        return serial.Serial

    def _connect(self):
        if self.serial_connection and self.serial_connection.is_open:
            return True

        now = time.monotonic()

        if now - self.last_connect_attempt < self.reconnect_delay:
            return False

        self.last_connect_attempt = now

        for port in self.ports:
            try:
                self.serial_connection = self.serial_factory(
                    port=port,
                    baudrate=self.baud_rate,
                    timeout=self.timeout,
                )
                self.active_port = port
                logger.info("ESP32 RFID reader connected on %s", port)
                return True
            except Exception as exc:
                logger.warning("Could not open ESP32 RFID reader on %s: %s", port, exc)

        self.serial_connection = None
        self.active_port = None
        return False

    def _disconnect(self):
        if not self.serial_connection:
            return

        try:
            self.serial_connection.close()
        except Exception as exc:
            logger.warning("Error closing ESP32 RFID serial port: %s", exc)
        finally:
            self.serial_connection = None
            self.active_port = None

    def _extract_uid(self, raw_data):
        if not raw_data:
            return None

        if isinstance(raw_data, bytes):
            value = raw_data.decode("utf-8", errors="ignore")
        else:
            value = str(raw_data)

        value = value.strip().upper()

        if not value:
            return None

        # ESP32 boot/debug lines such as "rst:0x1" or "SPI_FAST_FLASH_BOOT"
        # are intentionally ignored here. Only clean RFID UID payloads pass.
        if not self.uid_pattern.fullmatch(value):
            logger.debug("Ignoring non-RFID serial line: %r", value)
            return None

        return value

    def read_uid(self):
        if not self._connect():
            return None

        try:
            return self._extract_uid(self.serial_connection.readline())
        except Exception as exc:
            logger.warning("ESP32 RFID read failed on %s: %s", self.active_port, exc)
            self._disconnect()
            return None

    def close(self):
        self._disconnect()
