class WearManifold:
    def __init__(self, limit=3810000):
        # 16-byte struct: [NodeID(8), ArchardWearVolume(8)]
        self.wear_state = bytearray(limit * 16)

    def enforce_contact_bounds(self):
        pass
