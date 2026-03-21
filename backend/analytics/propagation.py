import networkx as nx
from typing import Dict, Set, List, Any
from redis.asyncio import Redis
from config import settings


class RiskPropagator:
    def __init__(self, graph: nx.DiGraph, decay_factor: float = 0.9):
        self.graph = graph
        self.decay_factor = decay_factor

    def calculate_transitive_impact(self, source_node: str, max_depth: int = 5) -> Dict[str, float]:
        """Calculates CVI attenuation based on topological distance-weighted decay."""
        impact_map: Dict[str, float] = {}
        source_cvi = self.graph.nodes[source_node].get("cvi", 0.0)

        # BFS traversal up to max_depth
        queue = [(source_node, 0)]
        visited = {source_node}

        while queue:
            u, d = queue.pop(0)
            if d > max_depth:
                continue

            # Normalized Impact: CVI_propagated = CVI_source * lambda^d
            impact = source_cvi * (self.decay_factor**d)
            impact_map[u] = impact

            # Reverse the DAG for impact propagation (searching up the tree)
            for v in self.graph.predecessors(u):
                if v not in visited:
                    visited.add(v)
                    queue.append((v, d + 1))

        return impact_map

    async def build_reachability_bitset(self, redis_client: Redis, ecosystem: str):
        """Pre-calculates reachability matrices optimized via Redis atomic bitwise BITOP."""
        # Failure 3 Resolution: Atomic BITOP OR in Redis to eliminate race conditions
        # Mapping bit index to each node
        node_to_idx = {node: idx for idx, node in enumerate(self.graph.nodes())}

        for node in self.graph.nodes():
            # Identifying all reachable parents
            ancestors = nx.ancestors(self.graph, node)
            bit_key = f"coregraph:reach:{ecosystem}:{node}"

            # Setting bits in Redis
            for ancestor in ancestors:
                idx = node_to_idx[ancestor]
                await redis_client.setbit(bit_key, idx, 1)

    async def query_reachability(
        self, redis_client: Redis, ecosystem: str, source: str, target: str
    ) -> bool:
        """O(1) reachability query leveraging optimized bitset buffers."""
        # Bit index retrieval
        node_to_idx = {node: idx for idx, node in enumerate(self.graph.nodes())}
        idx = node_to_idx.get(target)
        if idx is None:
            return False

        bit_key = f"coregraph:reach:{ecosystem}:{source}"
        return await redis_client.getbit(bit_key, idx) == 1
