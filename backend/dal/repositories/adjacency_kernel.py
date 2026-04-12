import struct


class AdjacencyKernel:
    def __init__(self, max_nodes=4000000, max_edges=10000000):
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.row_ptr = bytearray((max_nodes + 1) * 4)
        self.col_idx = bytearray(max_edges * 4)
        self.edge_count = 0

    def build_csr(self, edges):
        counts = [0] * self.max_nodes
        for u, v in edges:
            counts[u] += 1

        ptr = 0
        for i in range(self.max_nodes):
            struct.pack_into("I", self.row_ptr, i * 4, ptr)
            ptr += counts[i]
        struct.pack_into("I", self.row_ptr, self.max_nodes * 4, ptr)

        curr = [struct.unpack_from("I", self.row_ptr, i * 4)[0] for i in range(self.max_nodes)]
        for u, v in edges:
            pos = curr[u]
            struct.pack_into("I", self.col_idx, pos * 4, v)
            curr[u] += 1
        self.edge_count = len(edges)

    def get_neighbors(self, node_id):
        start = struct.unpack_from("I", self.row_ptr, node_id * 4)[0]
        end = struct.unpack_from("I", self.row_ptr, (node_id + 1) * 4)[0]
        neighbors = []
        for i in range(start, end):
            neighbors.append(struct.unpack_from("I", self.col_idx, i * 4)[0])
        return neighbors
