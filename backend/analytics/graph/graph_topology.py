from backend.dal.repositories.adjacency_kernel import AdjacencyKernel


class GraphTopologyManifold:
    def __init__(self, max_nodes=4000000):
        self.adjacency = AdjacencyKernel(max_nodes=max_nodes)

    def ingest_topology(self, edges):
        self.adjacency.build_csr(edges)

    def verify_reachability(self, start_node, target_node, depth_limit=3):
        if start_node == target_node:
            return True
        visited = set([start_node])
        q = [start_node]
        depth = 0

        while q and depth < depth_limit:
            next_q = []
            for u in q:
                for v in self.adjacency.get_neighbors(u):
                    if v == target_node:
                        return True
                    if v not in visited:
                        visited.add(v)
                        next_q.append(v)
            q = next_q
            depth += 1
        return False
