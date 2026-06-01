from abc import ABC, abstractmethod


class RFIDReader(ABC):
    @abstractmethod
    def read_uid(self):
        """Return one scanned RFID UID/tag as a string, or None when no scan is available."""
        raise NotImplementedError

    def close(self):
        """Release hardware resources. Mock readers may leave this as a no-op."""
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
        return False
