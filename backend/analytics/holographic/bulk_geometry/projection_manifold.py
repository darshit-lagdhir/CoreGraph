class RelationalProjectionManifold:
    def __init__(self, capacity: int):
        self.capacity = capacity
        # 16 bytes per state: [8: bulk_node_id, 4: conformal_weight, 4: holographic_entropy]
        self._firmament = bytearray(capacity * 16)
        self._view = memoryview(self._firmament)

    def map_dual_hologram(self, index: int, bulk_node: int, conformal_weight: float):
        offset = index * 16
        self._firmament[offset : offset + 8] = bulk_node.to_bytes(8, "little")
        # Simulate storing localized conformal boundary projection
        self._firmament[offset + 8 : offset + 12] = int(conformal_weight * 1e6).to_bytes(
            4, "little", signed=True
        )
