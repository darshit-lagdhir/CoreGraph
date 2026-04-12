class SurpriseEngine:
    def __init__(self, limit=1000000):
        # 16-byte fixed struct: [NodeID, ShannonEntropy, NoveltyScore, ConditionalUncertainty]
        self.surprise_buffer = bytearray(limit * 16)

    def calculate_bit_density(self):
        pass
