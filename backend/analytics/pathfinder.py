import networkx as nx
import heapq
from typing import Dict, List, Optional, Tuple, Set, Any


class Pathfinder:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        # Failure 2 Resolution: Pre-allocated object pool for search state
        # These buffers are reused to eliminate garbage collection creep during high-volume queries
        self._visited: Set[str] = set()
        self._priority_queue: List[Tuple[float, str]] = []
        self._distances: Dict[str, float] = {}
        self._predecessors: Dict[str, Optional[str]] = {}

    def _reset_buffers(self) -> None:
        """Flushes the static memory buffer for a clean search state."""
        self._visited.clear()
        self._priority_queue.clear()
        self._distances.clear()
        self._predecessors.clear()

    def dijkstra(self, source: str, target: str) -> List[str]:
        """Finds the absolute shortest path using centrality-weighted edge costs."""
        self._reset_buffers()

        if source not in self.graph or target not in self.graph:
            return []

        self._distances[source] = 0.0
        heapq.heappush(self._priority_queue, (0.0, source))

        while self._priority_queue:
            current_dist, u = heapq.heappop(self._priority_queue)

            if u == target:
                return self._reconstruct_path(target)

            if u in self._visited:
                continue
            self._visited.add(u)

            for v in self.graph.neighbors(u):
                # Dijkstra Cost Function: favoring high-centrality (low dist) paths
                # W_uv = 1 + (1 / (1 + PageRank_v))
                pagerank_v = self.graph.nodes[v].get("pagerank", 1e-6)
                weight = 1.0 + (1.0 / (1.0 + pagerank_v))

                new_dist = current_dist + weight
                if new_dist < self._distances.get(v, float("inf")):
                    self._distances[v] = new_dist
                    self._predecessors[v] = u
                    heapq.heappush(self._priority_queue, (new_dist, v))

        return []

    def a_star(self, source: str, target: str) -> List[str]:
        """Optimized A* search utilizing topological depth as an admissible heuristic."""
        self._reset_buffers()

        if source not in self.graph or target not in self.graph:
            return []

        # Pre-calculating depths if not already present
        # h(n) = max(0, depth_target - depth_n) - Failure 1 Resolution: Admissible Lower Bound
        target_depth = self.graph.nodes[target].get("depth", 0)

        self._distances[source] = 0.0
        # g(n) = cost, f(n) = g(n) + h(n)
        initial_h = max(0, target_depth - self.graph.nodes[source].get("depth", 0))
        heapq.heappush(self._priority_queue, (initial_h, source))

        while self._priority_queue:
            f_score, u = heapq.heappop(self._priority_queue)

            if u == target:
                return self._reconstruct_path(target)

            if u in self._visited:
                continue
            self._visited.add(u)

            g_u = self._distances[u]
            for v in self.graph.neighbors(u):
                pagerank_v = self.graph.nodes[v].get("pagerank", 1e-6)
                weight = 1.0 + (1.0 / (1.0 + pagerank_v))

                g_v = g_u + weight
                if g_v < self._distances.get(v, float("inf")):
                    self._distances[v] = g_v
                    self._predecessors[v] = u
                    h_v = max(0, target_depth - self.graph.nodes[v].get("depth", 0))
                    f_v = g_v + h_v
                    heapq.heappush(self._priority_queue, (f_v, v))

        return []

    def _reconstruct_path(self, target: str) -> List[str]:
        """Backtracks from the target node using the predecessor map."""
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = self._predecessors.get(current)
        return path[::-1]

    def bidirectional_bfs(self, source: str, target: str) -> List[str]:
        """High-velocity cross-ecosystem discovery traversing O(b^(d/2)) nodes."""
        if source == target:
            return [source]

        q_f = [source]
        q_b = [target]
        visited_f = {source: None}
        visited_b = {target: None}

        while q_f and q_b:
            # Forward step
            u_f = q_f.pop(0)
            for v in self.graph.successors(u_f):
                if v in visited_b:
                    return self._join_bidirectional(visited_f, visited_b, u_f, v)
                if v not in visited_f:
                    visited_f[v] = u_f
                    q_f.append(v)

            # Backward step
            u_b = q_b.pop(0)
            for v in self.graph.predecessors(u_b):
                if v in visited_f:
                    return self._join_bidirectional(visited_f, visited_b, v, u_b)
                if v not in visited_b:
                    visited_b[v] = u_b
                    q_b.append(v)

        return []

    def _join_bidirectional(
        self, v_f: Dict[str, Any], v_b: Dict[str, Any], middle_f: str, middle_b: str
    ) -> List[str]:
        """Stitches the forward and backward paths into a single topological thread."""
        path_f = []
        curr = middle_f
        while curr is not None:
            path_f.append(curr)
            curr = v_f[curr]
        path_f = path_f[::-1]

        path_b = []
        curr = middle_b
        while curr is not None:
            path_b.append(curr)
            curr = v_b[curr]

        return path_f + path_b
