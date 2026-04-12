import struct


class Package:
    pass


class PackageVersion:
    pass


class DependencyEdge:
    pass


class BinarySchemaValidator:
    def __init__(self):
        self.struct_format = ">32sIf"
        self.record_size = struct.calcsize(self.struct_format)

    def validate(self, block: bytes) -> bool:
        return len(block) == self.record_size

    def pack_node(self, node_id: bytes, type_code: int, weight: float) -> bytes:
        return struct.pack(self.struct_format, node_id.ljust(32, b"\x00"), type_code, weight)
