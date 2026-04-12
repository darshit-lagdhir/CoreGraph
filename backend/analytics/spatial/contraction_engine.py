import struct


class ContractionEngine:
    def __init__(self, max_clusters=65536):
        self.max_clusters = max_clusters
        self.record_size = 32
        self.pool = bytearray(self.max_clusters * self.record_size)

    def accumulate(self, cid: int, x: float, y: float, w: float):
        if cid >= self.max_clusters:
            raise OverflowError("CentroidOverflow")
        offset = cid * self.record_size
        sx, sy, sw, count = struct.unpack_from("<dddQ", self.pool, offset)
        struct.pack_into("<dddQ", self.pool, offset, sx + (x * w), sy + (y * w), sw + w, count + 1)

    def get_centroid(self, cid: int):
        offset = cid * self.record_size
        sx, sy, sw, count = struct.unpack_from("<dddQ", self.pool, offset)
        if count == 0:
            return (0.0, 0.0, 0.0, 0)
        return (sx / sw, sy / sw, sw, count)
