import struct


class BitwiseTilingEngine:
    def coord_to_morton(self, x: float, y: float) -> int:
        ix, iy = int(abs(x) * 10000), int(abs(y) * 10000)
        ix = (ix | (ix << 8)) & 0x00FF00FF
        ix = (ix | (ix << 4)) & 0x0F0F0F0F
        ix = (ix | (ix << 2)) & 0x33333333
        ix = (ix | (ix << 1)) & 0x55555555
        iy = (iy | (iy << 8)) & 0x00FF00FF
        iy = (iy | (iy << 4)) & 0x0F0F0F0F
        iy = (iy | (iy << 2)) & 0x33333333
        iy = (iy | (iy << 1)) & 0x55555555
        return ix | (iy << 1)

    def generate_tile_sig(self, x: float, y: float, depth: int) -> bytes:
        m = self.coord_to_morton(x, y)
        return struct.pack(">IQ", depth, m)
