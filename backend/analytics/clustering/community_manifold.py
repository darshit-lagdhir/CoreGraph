class CommunityManifold:
    def __init__(self, limit=1000000):
        # 16-byte fixed struct: [NodeID, CommunityID, ModularityDelta, ResolutionIndex]
        self.affiliation_buffer = bytearray(limit * 16)

    def map_memberships(self):
        pass
