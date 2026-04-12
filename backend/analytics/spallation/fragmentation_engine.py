class FragmentationEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), EjectaVelocity(8), HugoniotLimit(8)]
        self.frag_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_spallation_ejecta(self):
        pass
