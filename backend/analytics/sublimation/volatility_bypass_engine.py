class VolatilityBypassEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), SublimationRate(8), EnthalpyPhase(8)]
        self.volatility_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_phase_bypass(self):
        pass
