import math
class VectorizedEntropyEngine:
    def calculate_shannon(self, payload: bytes) -> float:
        if not payload: return 0.0
        freq = {}
        for b in payload:
            freq[b] = freq.get(b, 0) + 1
        ent = 0.0
        length = len(payload)
        for count in freq.values():
            p = count / length
            ent -= p * math.log2(p)
        return ent
