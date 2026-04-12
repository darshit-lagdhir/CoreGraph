class InterfaceFrictionEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), FrictionCoefficient(8), RelationalWear(8)]
        self.friction_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_interfacial_drag(self):
        pass
