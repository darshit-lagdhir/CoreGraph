import heapq, struct


class DistributedHeuristicPathfinderManifold:
    def __init__(self):
        self.edges = {}

    def add_edge(self, src: int, dst: int, weight: float):
        if src not in self.edges:
            self.edges[src] = []
        self.edges[src].append((dst, weight))

    def shortest_path(self, start: int, target: int):
        pq = [(0.0, start, [])]
        visited = set()
        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            path = path + [node]
            if node == target:
                return cost, path
            for nxt, w in self.edges.get(node, []):
                if nxt not in visited:
                    heapq.heappush(pq, (cost + w, nxt, path))
        return float("inf"), []
