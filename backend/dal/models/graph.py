class Package:
    pass


class PackageVersion:
    pass


class DependencyEdge:
    pass


class ContiguousGraphModel:
    def __init__(self, capacity=10485760):
        self.node_buffer = bytearray(capacity)
        self.cursor = 0
        self.node_count = 0

    def append_node(self, node_bytes: bytes) -> int:
        l = len(node_bytes)
        if self.cursor + l > len(self.node_buffer):
            raise MemoryError("Graph Buffer Overflow")
        self.node_buffer[self.cursor : self.cursor + l] = node_bytes
        self.cursor += l
        self.node_count += 1
        return self.cursor
