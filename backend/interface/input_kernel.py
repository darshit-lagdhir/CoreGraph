import struct


class InteractionKernel:
    def __init__(self, capacity=1048576):
        self.capacity = capacity
        # Event struct: Q (timestamp), f (x), f (y), I (event_type), I (node_id)
        self.fmt = "QffII"
        self.record_size = struct.calcsize(self.fmt)
        self.buffer = bytearray(self.capacity * self.record_size)
        self.cursor = 0

    def register_event(self, timestamp: int, x: float, y: float, event_type: int, node_id: int):
        struct.pack_into(
            self.fmt,
            self.buffer,
            self.cursor * self.record_size,
            timestamp,
            x,
            y,
            event_type,
            node_id,
        )
        self.cursor += 1

    def process_event(self, index: int):
        return struct.unpack_from(self.fmt, self.buffer, index * self.record_size)
