import random
import time

from app.hardware.base_reader import RFIDReader


class MockRFIDReader(RFIDReader):
    def __init__(self, tags=None, delay_seconds=0):
        self.tags = list(tags or [])
        self.delay_seconds = delay_seconds

    def read_uid(self):
        if self.delay_seconds:
            time.sleep(self.delay_seconds)

        if not self.tags:
            return None

        return random.choice(self.tags)
