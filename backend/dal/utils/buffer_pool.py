from backend.core.memory_manager import MemoryManager


class BufferPool:
    def __init__(self, memory_manager: MemoryManager, size: int):
        self.offset = memory_manager.allocate(size)
        self.size = size
        self.heap_ref = memory_manager.heap
