import struct
class StreamingKernel:
    def __init__(self, capacity=10000):
        self.capacity = capacity
        self.record_size = 24
        self.pool = bytearray(self.capacity * self.record_size)
        self.sequence_id = 0
        self.cursor = 0
    def emit_delta(self, node_id: int, state_flag: int, dx: float, dy: float):
        if self.cursor >= self.capacity:
            raise OverflowError('SequenceBoundaryBreached')
        seq = self.sequence_id
        offset = self.cursor * self.record_size
        struct.pack_into('<QIIff', self.pool, offset, seq, node_id, state_flag, dx, dy)
        self.sequence_id += 1
        self.cursor += 1
        return seq
    def get_delta(self, idx: int):
        return struct.unpack_from('<QIIff', self.pool, idx * self.record_size)
