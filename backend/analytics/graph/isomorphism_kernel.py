import struct


class IsomorphismKernel:
    def __init__(self, max_depth=100000):
        self.max_depth = max_depth
        self.record_size = 16
        self.stack = bytearray(self.max_depth * self.record_size)
        self.sp = 0

    def push(self, depth: int, q_node: int, t_node: int, state: int):
        if self.sp >= self.max_depth:
            raise OverflowError("PatternOverflow")
        offset = self.sp * self.record_size
        struct.pack_into("<IIII", self.stack, offset, depth, q_node, t_node, state)
        self.sp += 1

    def pop(self):
        if self.sp == 0:
            return None
        self.sp -= 1
        return struct.unpack_from("<IIII", self.stack, self.sp * self.record_size)
