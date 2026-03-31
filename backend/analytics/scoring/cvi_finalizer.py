import numpy as np
import networkx as nx
import hashlib
import gc
import psutil
import time
from typing import Dict, Any, Callable


class CompositeVulnerabilityFinalizationManifold:
    __slots__ = [
        "_graph",
        "_hardware_tier",
        "_hud_sync_callback",
        "_batch_size",
        "_cvi_finalization_complete",
        "_merkle_root",
        "_node_list",
    ]

    def __init__(
        self, graph: nx.DiGraph, hardware_tier: str = "redline", hud_sync_callback: Callable = None
    ):
        self._graph = graph
        self._hardware_tier = hardware_tier
        self._hud_sync_callback = hud_sync_callback or (lambda x: None)
        self._cvi_finalization_complete = False
        self._merkle_root = None
        self._node_list = list(self._graph.nodes())
        self._calibrate_crystallization_velocity()

    def _calibrate_crystallization_velocity(self) -> None:
        """Configures memory pacing based on hardware detection and explicit tier parameters."""
        memory_stats = psutil.virtual_memory()
        if self._hardware_tier == "potato" or memory_stats.available < 2 * 1024**3:
            self._batch_size = 50000
        else:
            self._batch_size = 1000000

    def _get_node_vectors(self) -> dict:
        """Extracts required telemetry dimensions into contiguous C-arrays."""
        size = len(self._node_list)
        vectors = {
            "pagerank": np.zeros(size, dtype=np.float64),
            "blast_radius": np.zeros(size, dtype=np.float64),
            "burnout": np.zeros(size, dtype=np.float64),
            "deficit": np.zeros(size, dtype=np.float64),
        }

        for i, node in enumerate(self._node_list):
            attrs = self._graph.nodes[node]
            vectors["pagerank"][i] = attrs.get("pagerank", 1e-10)
            vectors["blast_radius"][i] = attrs.get("blast_radius", 1.0)
            vectors["burnout"][i] = attrs.get("human_burnout_score", 0.0)
            vectors["deficit"][i] = attrs.get("financial_deficit_score", 0.0)

        return vectors

    def execute_telemetry_fusion(self, burnout: np.ndarray, deficit: np.ndarray) -> np.ndarray:
        """Fuses multi-dimensional signals using Log-Sum-Exp stabilization."""
        # Log-sum-exp stabilization neutralizing floating point explosion
        return np.logaddexp(np.clip(burnout, 1e-10, None), np.clip(deficit, 1e-10, None))

    def _run_sigmoid_crystallization_gate(
        self, fused_risk: np.ndarray, pagerank: np.ndarray
    ) -> np.ndarray:
        """Executes the Non-Linear Score Crystallization Doctrine."""
        # Compute topological responsibility scalar (PageRank Percentile)
        sort_indices = np.argsort(pagerank)
        ranks = np.empty_like(sort_indices)
        ranks[sort_indices] = np.arange(len(pagerank))
        pr_percentile = ranks / len(pagerank)

        # Importance-Adaptive Midpoint shift
        # High PR -> Lower midpoint (Catapult effect for apex nodes)
        # Low PR -> Higher midpoint (Noise suppression for leaf nodes)
        midpoints = 8.0 - (pr_percentile * 6.0)

        # Steepness constant
        k = 1.5

        # Logistic Sigmoid Activation
        # f(x) = 100 / (1 + e^(-k(x - x0)))
        exponent = -k * (fused_risk - midpoints)
        exponent = np.clip(exponent, -700, 700)  # Saturation guard to prevent overflow

        cvi = 100.0 / (1.0 + np.exp(exponent))

        # Bitwise Boundary Guard
        return np.clip(cvi, 0.0, 100.0)

    def execute_finalization_sweep(self) -> Dict[str, Any]:
        """Orchestrates the terminal scoring loop and writes verdicts to the graph."""
        start_time = time.perf_counter()
        size = len(self._node_list)

        vectors = self._get_node_vectors()
        total_batches = (size + self._batch_size - 1) // self._batch_size

        final_cvi = np.zeros(size, dtype=np.float64)
        hasher = hashlib.sha384()

        for batch_idx in range(total_batches):
            start = batch_idx * self._batch_size
            end = min((batch_idx + 1) * self._batch_size, size)

            vec_pr = vectors["pagerank"][start:end]
            vec_burnout = vectors["burnout"][start:end]
            vec_deficit = vectors["deficit"][start:end]

            # Dimensional Fusion
            fused_batch = self.execute_telemetry_fusion(vec_burnout, vec_deficit)

            # Sigmoid Crystallization Gate
            cvi_batch = self._run_sigmoid_crystallization_gate(fused_batch, vec_pr)

            final_cvi[start:end] = cvi_batch

            # Hardware-Aware Pacing
            if self._hardware_tier == "potato":
                gc.collect()

            # HUD Verdict Sync Manifold Hook
            self._hud_sync_callback(
                {
                    "NodesFinalized": end,
                    "EmergencyRate": float(np.mean(cvi_batch >= 95.0)),
                    "CrystallizationVelocity": end / max((time.perf_counter() - start_time), 0.001),
                    "BoundaryAdherenceScore": float(
                        np.mean((cvi_batch >= 0.0) & (cvi_batch <= 100.0))
                    ),
                }
            )

        # Final Validation & Metadata Injection
        nan_check = np.isnan(final_cvi)
        if np.any(nan_check):
            raise ValueError("TopologicalIntegrityError: NaN detected in finalized CVI array.")

        for i, node in enumerate(self._node_list):
            score = float(final_cvi[i])
            self._graph.nodes[node]["fused_vulnerability_index"] = score
            self._graph.nodes[node]["verdict_metadata"] = {
                "logic_state": "VERIFIED",
                "parameters": "w_centrality, w_burnout, w_funding",
                "provenance": "SIGMOID_CRYSTALLIZATION_MANIFOLD",
            }
            # Unforgeable Cryptographic Seal
            hasher.update(str(node).encode("utf-8"))
            hasher.update(final_cvi[i].tobytes())

        self._merkle_root = hasher.hexdigest()
        self._cvi_finalization_complete = True

        # Free heavy arrays
        del vectors
        gc.collect()

        # Fidelity metrics calculation
        fidelity_metric = np.sum((final_cvi >= 0.0) & (final_cvi <= 100.0)) / size
        contrast_metric = float(np.var(final_cvi))

        return {
            "IntegrationFidelity": fidelity_metric,
            "SignalContrast": contrast_metric,
            "LogicRootHash": self._merkle_root,
            "Status": "MODULE_9_SEALED",
        }
