import struct
class PartitioningEngine:
    def __init__(self, limit=1000000):
        # 32 bytes per node: x, y, id, parent, tl, tr, bl, br
        self.heap = bytearray(limit * 32)
        self.cursor = 0
    def alloc(self):
        idx = self.cursor
        self.cursor += 32
        return idx
