class InterfacialSeparationEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), PeelIntensity(8), CZMLimit(8)]
        self.separation_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_shear_separation(self):
        pass
