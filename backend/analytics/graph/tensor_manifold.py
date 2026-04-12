class SignalBuffer:
    def __init__(self):
        self.buffer = bytearray(1024 * 1024)
        self.ptr = 0
    def ingest(self, signal: bytes):
        l = len(signal)
        if self.ptr + l > len(self.buffer): self.ptr = 0
        self.buffer[self.ptr:self.ptr+l] = signal
        self.ptr += l
