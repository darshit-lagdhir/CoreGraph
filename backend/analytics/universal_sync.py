import ctypes


class UniversalIntegritySync:
    def __init__(self):
        self._sync_block = bytearray(8192)
        self._view = memoryview(self._sync_block)

    def lock_hardening(self, index: int):
        self._sync_block[index % 8192] = 1

    def release_hardening(self, index: int):
        self._sync_block[index % 8192] = 0

    def verify_stationarity_state(self, index: int) -> bool:
        return self._sync_block[index % 8192] == 0
