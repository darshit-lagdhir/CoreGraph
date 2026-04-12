class RelationalStationarityManifold:
    def __init__(self, capacity: int):
        self.capacity = capacity
        # 16 bytes per state: [8: sovereign_id, 4: architectural_weight, 4: finality_entropy]
        self._firmament = bytearray(capacity * 16)
        self._view = memoryview(self._firmament)

    def map_sovereign_state(self, index: int, sovereign_node: int, weight: float):
        offset = index * 16
        self._firmament[offset : offset + 8] = sovereign_node.to_bytes(8, "little")
        # Simulate storing localized absolute finality weight
        self._firmament[offset + 8 : offset + 12] = int(weight * 1e6).to_bytes(
            4, "little", signed=True
        )
