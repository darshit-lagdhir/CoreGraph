class BinaryMaterializer:
    def __init__(self, capacity=1048576):
        self.wal_buffer = bytearray(capacity)
        self.cursor = 0

    def flush_record(self, payload: bytes) -> int:
        l = len(payload)
        if self.cursor + l > len(self.wal_buffer):
            self.cursor = 0
        start = self.cursor
        self.wal_buffer[self.cursor : self.cursor + l] = payload
        self.cursor += l
        return start
