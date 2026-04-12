import struct
from backend.analytics.temporal.causality_engine import CausalityEngine
class LineageReconstructor:
    def __init__(self, engine: CausalityEngine):
        self.engine = engine
    def trace_lineage(self, start_idx: int):
        lineage = []
        curr = start_idx
        while curr < self.engine.cursor:
            ts, p, c = self.engine.get_event(curr)
            lineage.append((ts, p, c))
            curr += 1
        return lineage
