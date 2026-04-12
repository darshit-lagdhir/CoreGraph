class ErosiveConsumptionEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), MassLossRate(8), CharringAblationLimit(8)]
        self.consumption_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_thermal_erosion(self):
        pass
