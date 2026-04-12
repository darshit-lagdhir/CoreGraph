import struct
class CausalityEngine:
    def __init__(self, capacity=3810000):
        self.capacity = capacity
        self.record_size = 16
        self.pool = bytearray(capacity * self.record_size)
        self.cursor = 0
        self.last_ts = 0
    def register_event(self, ts: int, parent_id: int, child_id: int):
        if self.cursor >= self.capacity:
            raise OverflowError('ChronosBoundaryBreached')
        if ts < self.last_ts:
            raise ValueError('CausalityDrift: Out of order timestamp')
        offset = self.cursor * self.record_size
        struct.pack_into('<QII', self.pool, offset, ts, parent_id, child_id)
        self.cursor += 1
        self.last_ts = ts
    def get_event(self, idx: int):
        if idx >= self.cursor: return None
        return struct.unpack_from('<QII', self.pool, idx * self.record_size)
