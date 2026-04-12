import struct


class AdjacencyBuffer:
    def __init__(self, max_nodes=1024):
        self.matrix = bytearray(max_nodes * max_nodes * 4)
        self.stride = max_nodes

    def set_weight(self, src: int, dst: int, weight: float):
        idx = (src * self.stride + dst) * 4
        self.matrix[idx : idx + 4] = struct.pack(">f", weight)

    def get_weight(self, src: int, dst: int) -> float:
        idx = (src * self.stride + dst) * 4
        return struct.unpack(">f", self.matrix[idx : idx + 4])[0]
