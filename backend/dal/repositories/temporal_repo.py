class TemporalBuffer:
    def __init__(self, size=1024 * 1024):
        self.buffer = bytearray(size)
        self.ptr = 0

    def append_event(self, event_data: bytes):
        l = len(event_data)
        if self.ptr + l > len(self.buffer):
            self.ptr = 0
        self.buffer[self.ptr : self.ptr + l] = event_data
        self.ptr += l
