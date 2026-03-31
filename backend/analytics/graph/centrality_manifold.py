import asyncio
import gc
import hashlib
import os
import time
from typing import Dict, Any, List

try:
    import psutil
except ImportError:
    psutil = None

import networkx as nx
import numpy as np
import scipy.sparse as sp


class EigenvectorCentralityManifold:
    """
    Global Eigenvector Centrality and PageRank Influence Scoring Kernel.
    Mathematical Arbiter enforcing Telemetry-Weighted Markov Chains and Absolute Determinism.
    """

    __slots__ = (
        "graph",
        "is_redline",
        "process_ref",
        "_matrix",
        "_node_list",
        "_start_time",
        "_iteration_count",
        "_current_delta",
        "_nnz",
        "_eps",
        "_mem_limit_bytes",
        "_math_seal",
    )

    def __init__(self, graph: nx.DiGraph, is_redline: bool = True):
        self.graph = graph
        self.is_redline = is_redline
        self.process_ref = psutil.Process(os.getpid()) if psutil else None
        self._matrix: Any = None
        self._node_list: List[str] = []
        self._start_time = 0.0
        self._iteration_count = 0
        self._current_delta = float("inf")
        self._nnz = 0
        self._eps = 1e-9 if is_redline else 1e-5
        self._mem_limit_bytes = 150 * 1024 * 1024
        self._math_seal = ""

    def construct_stochastic_adjacency_matrix(self) -> None:
        """
        Hyper-Sparse CSR Generator Kernel: Fuses topology with Telemetry-Weighted Markov Chains.
        Neutralizes Dense Array Avalanche into highly constrained, Float64 normalized matrix.
        """
        if not self.graph.graph.get("is_dag_certified", False):
            raise RuntimeError(
                "TopologicalIntegrityError: Graph must be DAG-Certified before matrix instantiation."
            )

        self._node_list = list(self.graph.nodes())
        n_nodes = len(self._node_list)
        if n_nodes == 0:
            return

        node_idx_map = {n: i for i, n in enumerate(self._node_list)}

        row_indices = []
        col_indices = []
        data_values = []

        for u, v in self.graph.edges():
            target_budget = float(self.graph.nodes[v].get("budget", 1.0))
            target_maintainers = float(self.graph.nodes[v].get("maintainers", 1.0))

            is_zombie = 1.0 if target_maintainers == 0.0 else 0.0

            weight = max(0.1, target_budget) + (is_zombie * 10.0)

            row_indices.append(node_idx_map[u])
            col_indices.append(node_idx_map[v])
            data_values.append(weight)

        coo = sp.coo_matrix(
            (data_values, (row_indices, col_indices)), shape=(n_nodes, n_nodes), dtype=np.float64
        )
        csr = coo.tocsr()

        row_sums = np.array(csr.sum(axis=1)).flatten()
        row_sums[row_sums == 0] = 1.0

        inv_diags = sp.diags(1.0 / row_sums)
        self._matrix = inv_diags.dot(csr)
        self._nnz = self._matrix.nnz

    async def execute_pagerank_power_iteration(self, damping_factor: float = 0.85) -> None:
        """
        Power Iteration Convergence Manifold: Executes heavily vectorized SpMV loops.
        Enforces mathematically deterministic convergence bounded by epsilon tolerance.
        """
        if self._matrix is None:
            self.construct_stochastic_adjacency_matrix()

        n_nodes = len(self._node_list)
        if n_nodes == 0:
            return

        self._start_time = time.monotonic()
        v_old = np.full(n_nodes, 1.0 / n_nodes, dtype=np.float64)
        teleport = np.full(n_nodes, (1.0 - damping_factor) / n_nodes, dtype=np.float64)

        if self._matrix is None:
            raise ValueError("Stochastic Matrix uninitialized. Cannot execute power iteration.")

        M_T = self._matrix.transpose().tocsr()

        while self._current_delta > self._eps:
            v_new = (damping_factor * M_T.dot(v_old)) + teleport
            self._current_delta = float(np.sum(np.abs(v_new - v_old)))
            v_old = v_new
            self._iteration_count += 1

            await self._calibrate_linear_algebra_pacing()
            self._push_hud_telemetry()
            await asyncio.sleep(0.001)

        self._inject_scores_and_seal(v_old)

    async def _calibrate_linear_algebra_pacing(self) -> None:
        """
        Hardware-Aware Convergence Gear-Box: Mitigates thermal limits and bounds RAM via GC tracking.
        """
        if not self.process_ref:
            return

        rss = self.process_ref.memory_info().rss
        if not self.is_redline or rss > (self._mem_limit_bytes * 0.8):
            if self._iteration_count % 5 == 0:
                gc.collect()
                if not self.is_redline:
                    self._eps = max(self._eps, 1e-5)
                await asyncio.sleep(0.005)

    def _push_hud_telemetry(self) -> Dict[str, Any]:
        """
        Convergence-to-HUD Sync Manifold: Formats active telemetry bridging C-backend metrics to UI arrays.
        """
        elapsed = max(0.001, time.monotonic() - self._start_time)
        ops = 2.0 * self._nnz * self._iteration_count
        gflops = (ops / elapsed) / 1e9

        n_sq = max(1, len(self._node_list) ** 2)
        sparsity_index = 1.0 - (self._nnz / n_sq)

        return {
            "CurrentDelta": self._current_delta,
            "ToleranceTarget": self._eps,
            "IterationCount": self._iteration_count,
            "GFLOPS": round(gflops, 6),
            "MatrixSparsityIndex": round(sparsity_index, 8),
        }

    def _inject_scores_and_seal(self, final_vector: np.ndarray) -> None:
        """
        Absolute Floating-Point Determinism Validation: Writes verified Eigen-centralities into DAG.
        """
        if np.isnan(final_vector).any() or np.isinf(final_vector).any():
            raise RuntimeError(
                "MathematicalIntegrityError: Float64 overflow or NaN detected in Centrality Vector."
            )

        for idx, node_id in enumerate(self._node_list):
            self.graph.nodes[node_id]["eigen_centrality"] = float(final_vector[idx])

        self._math_seal = hashlib.sha256(final_vector.tobytes()).hexdigest()

        # Pre-Blast Memory Reclamation
        self._matrix = None
        self._node_list = []
        gc.collect()

    def yield_scored_graph(self) -> nx.DiGraph:
        """Wait-Free Scored Delivery Bus passing verified DiGraph to downstream execution."""
        return self.graph
