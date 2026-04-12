import struct
class AuthorityRepository:
    def __init__(self, node_capacity=3810000):
        self.capacity = node_capacity
        self.fmt = 'f'
        self.record_size = struct.calcsize(self.fmt)
        self.buffer = bytearray(self.capacity * self.record_size)
    def assign_score(self, index: int, score: float):
        struct.pack_into(self.fmt, self.buffer, index * self.record_size, score)
    def get_score(self, index: int) -> float:
        return struct.unpack_from(self.fmt, self.buffer, index * self.record_size)[0]
