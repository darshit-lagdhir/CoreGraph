import struct


class ClusteringKernel:
    @staticmethod
    def assign(x: float, y: float, grid_size: float) -> int:
        hx = int(x / grid_size)
        hy = int(y / grid_size)
        return (hx & 0xFFFF) | ((hy & 0xFFFF) << 16)
