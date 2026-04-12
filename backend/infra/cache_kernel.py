import struct
from backend.core.memory_manager import MemoryManager


class PhysicalCacheKernel:
    def __init__(self, memory_manager: MemoryManager, max_entries=3810000):
        self.record_size = 12
        self.capacity = max_entries
        self.offset = memory_manager.allocate(self.capacity * self.record_size)
        self.heap = memory_manager.heap

    def store(self, idx, node_id, ts):
        if idx >= self.capacity:
            raise IndexError("AllocationBoundaryBreached")
        struct.pack_into("<IQ", self.heap, self.offset + (idx * self.record_size), node_id, ts)

    def retrieve(self, idx):
        return struct.unpack_from("<IQ", self.heap, self.offset + (idx * self.record_size))
