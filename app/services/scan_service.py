import logging
import threading
import time
from datetime import datetime

from app.config import (
    RFID_MODE,
    RFID_DUPLICATE_WINDOW_SECONDS,
    RFID_POLL_INTERVAL_SECONDS,
)
from app.hardware import create_rfid_reader

logger = logging.getLogger(__name__)


class ScanService:
    def __init__(
        self,
        reader_factory=create_rfid_reader,
        poll_interval=RFID_POLL_INTERVAL_SECONDS,
        duplicate_window=RFID_DUPLICATE_WINDOW_SECONDS,
    ):
        self.reader_factory = reader_factory
        self.poll_interval = poll_interval
        self.duplicate_window = duplicate_window
        self.reader = None
        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.latest_scan = None
        self.last_uid = None
        self.last_uid_at = 0
        self.running = False

    def start_reader(self):
        if self.running:
            return

        self.stop_event.clear()
        self.running = True
        self.thread = threading.Thread(
            target=self._reader_loop,
            name="rfid-reader",
            daemon=True,
        )
        self.thread.start()
        logger.info("[RFID] Scan service started in %s mode", RFID_MODE)

    def stop_reader(self):
        if not self.running:
            return

        self.stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        if self.reader:
            try:
                self.reader.close()
            except Exception as exc:
                logger.warning("Error while closing RFID reader: %s", exc)

        self.reader = None
        self.thread = None
        self.running = False
        logger.info("RFID scan service stopped")

    def get_latest_scan(self):
        with self.lock:
            scan = self.latest_scan
            self.latest_scan = None

        return scan

    def clear_scan(self):
        with self.lock:
            self.latest_scan = None

    def _reader_loop(self):
        try:
            self.reader = self.reader_factory()
        except Exception as exc:
            logger.warning("RFID reader could not be initialized: %s", exc)
            self.running = False
            return

        while not self.stop_event.is_set():
            try:
                uid = self.reader.read_uid()

                if uid:
                    self._publish_scan(uid)
            except Exception as exc:
                logger.warning("RFID scan loop error: %s", exc)

            self.stop_event.wait(self.poll_interval)

    def _publish_scan(self, uid):
        now = time.monotonic()

        with self.lock:
            if (
                uid == self.last_uid
                and now - self.last_uid_at < self.duplicate_window
            ):
                logger.debug("[RFID] Duplicate scan suppressed: %s", uid)
                return

            self.last_uid = uid
            self.last_uid_at = now
            self.latest_scan = {
                "uid": uid,
                "scanned_at": time.time(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "mode": RFID_MODE,
            }
            logger.info("[RFID] UID detected: %s", uid)


scan_service = ScanService()
