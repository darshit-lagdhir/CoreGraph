class ViscosityEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), ReynoldsNumber(8), ShearStress(8)]
        self.flow_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_topological_viscosity(self):
        pass
