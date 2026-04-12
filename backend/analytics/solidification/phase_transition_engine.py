class PhaseTransitionEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), FreezingVelocity(8), LatentHeat(8)]
        self.transition_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_solidification_front(self):
        pass
