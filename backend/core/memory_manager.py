import struct
class MemoryManager:
    def __init__(self, capacity_bytes=157286400):
        self.capacity = capacity_bytes
        self.heap = bytearray(self.capacity)
        self.cursor = 0
    def allocate(self, size: int) -> int:
        if self.cursor + size > self.capacity:
            raise MemoryError('ResidencyOverflow')
        offset = self.cursor
        self.cursor += size
        return offset
    def reset_heap(self):
        self.cursor = 0
