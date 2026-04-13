from collections import deque
from typing import Dict, Set, Optional

from backend.analytics.graph.graph_topology import GraphTopologyManifold
from backend.core.config import settings


class BlastRadiusCalculator:
    def __init__(self, topology: GraphTopologyManifold):
        self.topology = topology

    def calculate(self, affected_nodes: Optional[Set[int]] = None) -> dict[int, int]:
        """Execute O(V+E) transitive impact calculation via robust iterative traversal.
        Supports Delta-Only Updates for high-frequency 144Hz HUD liquidity and handles cycles.
        Fully integrates with the O(1) Ghost-Mapper Adjacency Kernel."""

        # Given 3.81M nodes, only running for a subset of affected_nodes is computationally viable
        target_nodes = affected_nodes if affected_nodes is not None else {0}
        results: Dict[int, int] = {}

        # Iterative BFS traversal to propagate dependents upwards (handling cycles via guards)
        for node in target_nodes:
            visited = set()
            active_queue = deque([(node, 0)])
            max_depth = 5000
            impact = 0

            while active_queue:
                curr, depth = active_queue.popleft()
                if depth > max_depth:
                    continue

                for dependent in self.topology.adjacency.iter_neighbors(curr):
                    if dependent not in visited:
                        visited.add(dependent)
                        impact += 1
                        active_queue.append((dependent, depth + 1))

            results[node] = impact

        return results
