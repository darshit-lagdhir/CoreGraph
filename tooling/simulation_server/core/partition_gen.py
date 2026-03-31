import random
import uuid
from typing import List, Dict, Any

# Internal CoreGraph imports (Task 027 persistent paths)
import sys
import os
root = os.getcwd()
if root not in sys.path:
    sys.path.insert(0, root)

class PartitionGenerator:
    """
    S.U.S.E. Adversarial Partition Generator (Task 014).
    Injecting 'Dark Ecosystems' and 'Ghost Islands' for structural stress testing.
    """
    def __init__(self, seed: int = 1337):
        self.rng = random.Random(seed)

    def inject_ghost_island(self, size: int = 50, conductance: float = 0.01) -> List[Dict[str, Any]]:
        island_id = str(uuid.uuid4())[:8]
        nodes = []

        # Dense Internal Mesh (High Density)
        for i in range(size):
            purl = f"pkg:npm/ghost-node-{island_id}-{i}"
            deps = [f"pkg:npm/ghost-node-{island_id}-{self.rng.randint(0, size-1)}" for _ in range(3)]

            # Low External Conductance
            if self.rng.random() < conductance:
                deps.append("pkg:npm/reputable-core-lib")

            nodes.append({
                "purl": purl,
                "dependencies": deps,
                "community_tag": island_id,
                "is_adversarial": True
            })
        return nodes

if __name__ == "__main__":
    gen = PartitionGenerator()
    island = gen.inject_ghost_island(size=10)
    for node in island: print(f"[GHOST] Node: {node['purl']} | Internal-Deps: {len(node['dependencies'])}")
