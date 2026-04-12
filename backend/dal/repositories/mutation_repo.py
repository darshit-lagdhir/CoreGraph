class SynchronousMutationBuffer:
    def __init__(self):
        self._buffer = bytearray(1024 * 1024)
        self._ptr = 0

    def apply_delta(self, delta: bytes):
        l = len(delta)
        if self._ptr + l > len(self._buffer):
            self._ptr = 0
        self._buffer[self._ptr : self._ptr + l] = delta
        self._ptr += l
        return True
