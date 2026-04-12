class EntanglementEntropyManifold:
    def __init__(self, capacity: int):
        self.capacity = capacity
        # 16 bytes per state: [8: entangled_partner_id, 4: concurrence, 4: phase_angle]
        self._firmament = bytearray(capacity * 16)
        self._view = memoryview(self._firmament)

    def map_entangled_pair(self, index: int, partner: int, concurrence: float):
        offset = index * 16
        self._firmament[offset : offset + 8] = partner.to_bytes(8, "little")
        # Simulate storing localized non-local effect
        self._firmament[offset + 8 : offset + 12] = int(concurrence * 1e6).to_bytes(
            4, "little", signed=True
        )
