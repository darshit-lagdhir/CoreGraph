class VitalitySweeper:
    def __init__(self, capacity=1048576):
        self.registry = bytearray(capacity)
        self.cursor = 0

    def mark_healthy(self, size: int):
        if self.cursor + size > len(self.registry):
            self.cursor = 0
        self.registry[self.cursor : self.cursor + size] = b"\x01" * size
        self.cursor += size
