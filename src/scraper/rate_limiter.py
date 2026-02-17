import time

class RateLimiter:
    def __init__(self, min_interval_s: float = 0.8):
        self.min_interval_s = min_interval_s
        self._last = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self._last
        sleep_for = self.min_interval_s - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)
        self._last = time.time()