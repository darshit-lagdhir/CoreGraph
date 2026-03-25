import json
import random
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Internal CoreGraph imports (Task 027 persistent paths)
import sys
import os
root = os.getcwd()
if root not in sys.path:
    sys.path.insert(0, root)

class DeltaEvent(BaseModel):
    purl: str
    type: str # 'VERSION_ADD', 'FISCAL_DRIFT', 'TOPOLOGY_DRIFT'
    payload: Dict[str, Any]
    timestamp: float

class DeltaGenerator:
    """
    S.U.S.E. Delta Generator (Task 011).
    Architect of Evolution for the 3.88M node software ocean.
    """
    def __init__(self, seed: int = 1337):
        self.rng = random.Random(seed)
        self.target_purls = [f"pkg:npm/core-lib-{i}" for i in range(1000)] # Subset for simulation

    def generate_batch(self, count: int = 100) -> List[DeltaEvent]:
        batch = []
        for _ in range(count):
            purl = self.rng.choice(self.target_purls)
            event_type = self.rng.choice(['VERSION_ADD', 'FISCAL_DRIFT', 'TOPOLOGY_DRIFT'])
            
            if event_type == 'VERSION_ADD':
                payload = {"new_version": f"1.{self.rng.randint(0,10)}.{self.rng.randint(0,100)}"}
            elif event_type == 'FISCAL_DRIFT':
                payload = {"funding_delta": self.rng.uniform(-1000, 5000)}
            else:
                payload = {"new_dependency": f"pkg:npm/dep-{self.rng.randint(0,5000)}"}
                
            batch.append(DeltaEvent(
                purl=purl,
                type=event_type,
                payload=payload,
                timestamp=time.time()
            ))
        return batch

if __name__ == "__main__":
    gen = DeltaGenerator()
    events = gen.generate_batch(5)
    for e in events: print(f"[DELTA] {e.type} -> {e.purl}")
