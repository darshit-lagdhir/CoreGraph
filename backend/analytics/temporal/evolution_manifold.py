import bisect, struct
class ChronosManifold:
    def __init__(self):
        self._timeline = []
    def record_event(self, timestamp: float, event_sig: bytes):
        bisect.insort(self._timeline, (timestamp, event_sig))
    def replay(self, start_time: float, end_time: float) -> list:
        start_idx = bisect.bisect_left(self._timeline, (start_time, b''))
        end_idx = bisect.bisect_right(self._timeline, (end_time, b'\xff'*32))
        return self._timeline[start_idx:end_idx]
