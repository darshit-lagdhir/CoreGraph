from __future__ import annotations

from array import array
from collections.abc import Iterable, Sequence
from typing import Iterator


class AdjacencyKernel:
    __slots__ = ("max_nodes", "max_edges", "row_ptr", "col_idx", "edge_count", "_virtual_rows")

    def __init__(self, max_nodes=4000000, max_edges=10000000):
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.row_ptr = array("I", [0]) * (max_nodes + 1)
        self.col_idx = array("I", [0]) * max_edges
        self.edge_count = 0
        self._virtual_rows: dict[int, tuple[int, ...]] = {}

    def _validate_node(self, node_id: int) -> None:
        if node_id < 0 or node_id >= self.max_nodes:
            raise IndexError(f"node_id {node_id} outside kernel bounds {self.max_nodes}")

    def build_csr(self, edges: Iterable[tuple[int, int]]):
        if not isinstance(edges, Sequence):
            edges = tuple(edges)

        counts = array("I", [0]) * self.max_nodes
        for u, v in edges:
            self._validate_node(u)
            self._validate_node(v)
            counts[u] += 1

        ptr = 0
        for i in range(self.max_nodes):
            self.row_ptr[i] = ptr
            ptr += counts[i]
        self.row_ptr[self.max_nodes] = ptr

        curr = array("I", self.row_ptr)
        for u, v in edges:
            pos = curr[u]
            self.col_idx[pos] = v
            curr[u] += 1
        self.edge_count = len(edges)
        self._virtual_rows.clear()
        return self

    def register_virtual_neighbors(self, node_id: int, neighbors: Iterable[int]) -> None:
        self._validate_node(node_id)
        self._virtual_rows[node_id] = tuple(
            neighbor for neighbor in neighbors if 0 <= neighbor < self.max_nodes
        )

    def seed_virtual_neighbors(
        self, node_id: int, fanout: int = 6, salt: int = 0
    ) -> tuple[int, ...]:
        self._validate_node(node_id)
        state = (node_id ^ (salt << 1) ^ self.max_nodes) & 0xFFFFFFFF
        seeded = []
        for _ in range(max(0, fanout)):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            candidate = state % self.max_nodes
            if candidate != node_id:
                seeded.append(candidate)
        deduped = tuple(dict.fromkeys(seeded))
        self._virtual_rows[node_id] = deduped
        return deduped

    def get_neighbors(self, node_id):
        if node_id in self._virtual_rows:
            return self._virtual_rows[node_id]
        self._validate_node(node_id)
        start = self.row_ptr[node_id]
        end = self.row_ptr[node_id + 1]
        return memoryview(self.col_idx)[start:end]

    def get_neighbor_count(self, node_id: int) -> int:
        if node_id in self._virtual_rows:
            return len(self._virtual_rows[node_id])
        self._validate_node(node_id)
        return self.row_ptr[node_id + 1] - self.row_ptr[node_id]

    def iter_neighbors(self, node_id: int) -> Iterator[int]:
        for neighbor in self.get_neighbors(node_id):
            yield int(neighbor)
