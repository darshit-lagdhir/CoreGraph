import ctypes


class HolographicIntegritySync:
    def __init__(self):
        self._sync_block = bytearray(8192)
        self._view = memoryview(self._sync_block)

    def lock_projection(self, index: int):
        self._sync_block[index % 8192] = 1

    def release_projection(self, index: int):
        self._sync_block[index % 8192] = 0

    def verify_bulk_state(self, index: int) -> bool:
        return self._sync_block[index % 8192] == 0
