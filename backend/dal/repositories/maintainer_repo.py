import struct
class SyndicateRepository:
    def __init__(self, node_capacity=3810000):
        self.capacity = node_capacity
        self.fmt = 'I'
        self.record_size = struct.calcsize(self.fmt)
        self.buffer = bytearray(self.capacity * self.record_size)
    def assign_community(self, index: int, community_id: int):
        struct.pack_into(self.fmt, self.buffer, index * self.record_size, community_id)
    def get_community(self, index: int) -> int:
        return struct.unpack_from(self.fmt, self.buffer, index * self.record_size)[0]
