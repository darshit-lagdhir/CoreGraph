class BellInequalityKernel:
    def __init__(self):
        self._l1_cache = bytearray(16384)

    def apply_chsh_violation(self, node_view: memoryview, count: int):
        for i in range(min(count, 16384 // 24)):
            offset = i * 24
            # Simulate non-linear CHSH violation via atomic displacement
            val = int.from_bytes(node_view[offset + 16 : offset + 24], "little")
            shifted = (val ^ 0x0A0A0A0A) & 0xFFFFFFFFFFFFFFFF
            node_view[offset + 16 : offset + 24] = shifted.to_bytes(8, "little")
