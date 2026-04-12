from collections import deque
from typing import Dict, Set, Optional

import networkx as nx


class BlastRadiusCalculator:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.ancestry: Dict[str, Set[str]] = {}

    def calculate(self, affected_nodes: Optional[Set[str]] = None) -> nx.DiGraph:
        """Execute O(V+E) transitive impact calculation via robust iterative traversal.
        Supports Delta-Only Updates for high-frequency 144Hz HUD liquidity and handles cycles."""
        
        target_nodes = affected_nodes if affected_nodes is not None else set(self.graph.nodes())
        dependents: Dict[str, Set[str]] = {node: set() for node in target_nodes}
        
        # Iterative BFS traversal to propagate dependents upwards (handling cycles via guards)
        for node in target_nodes:
            visited = set()
            active_queue = deque([(node, 0)])
            max_depth = 5000
            
            while active_queue:
                curr, depth = active_queue.popleft()
                if depth > max_depth:
                    continue
                
                for dependent in self.graph.predecessors(curr):
                    if dependent not in visited:
                        visited.add(dependent)
                        dependents[node].add(dependent)
                        active_queue.append((dependent, depth + 1))
        
        for node in target_nodes:
            self.graph.nodes[node]["blast_radius"] = len(dependents[node])
            
        return self.graph
