import struct


class VectorSpaceModel:
    def __init__(self, node_capacity=3810000):
        self.capacity = node_capacity
        self.fmt = "fff"
        self.record_size = struct.calcsize(self.fmt)
        self.buffer = bytearray(self.capacity * self.record_size)

    def set_position(self, index: int, x: float, y: float, z: float):
        struct.pack_into(self.fmt, self.buffer, index * self.record_size, x, y, z)

    def get_position(self, index: int):
        return struct.unpack_from(self.fmt, self.buffer, index * self.record_size)


class PackageSpatialIndex:
    pass
