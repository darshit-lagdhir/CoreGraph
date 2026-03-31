import asyncio
import gc
import math
import os
import time
from typing import Dict, Any, List, Optional

try:
    import psutil
except ImportError:
    psutil = None

import networkx as nx
import numpy as np


class CompositeVulnerabilityPropagationManifold:
    """
    Downstream Blast Radius Propagation and Composite Vulnerability Index (CVI) Kernel.
    Apex Predictor enforcing Topologically Sorted Memoization and Non-Linear Sigmoid Fusion.
    """

    __slots__ = (
        "graph",
        "is_redline",
        "process_ref",
        "_start_time",
        "_nodes_processed",
        "_max_cvi_observed",
        "_mem_limit_bytes",
        "_attenuation_gamma",
        "_w_centrality",
        "_w_blast",
        "_w_finance",
        "_w_risk",
    )

    def __init__(self, graph: nx.DiGraph, is_redline: bool = True):
        self.graph = graph
        self.is_redline = is_redline
        self.process_ref = psutil.Process(os.getpid()) if psutil else None
        self._start_time = 0.0
        self._nodes_processed = 0
        self._max_cvi_observed = 0.0
        self._mem_limit_bytes = 150 * 1024 * 1024

        # Absolute Topological Friction Coefficient
        self._attenuation_gamma = 0.15

        # Heuristic Fusion Matrix Weights
        self._w_centrality = 0.40
        self._w_blast = 0.30
        self._w_finance = 0.20
        self._w_risk = 0.10

    async def execute_topological_blast_propagation(self) -> None:
        """
        Single-Pass Wavefront Kernel: Executes $O(V+E)$ downstream traversal via Topological Sort.
        Neutralizes Combinatorial Avalanche by deeply memoizing the accumulative threat payloads.
        """
        if not self.graph.graph.get("is_dag_certified", False):
            raise RuntimeError(
                "TopologicalIntegrityError: Graph must be DAG-Certified for CVI Propagation."
            )

        self._start_time = time.monotonic()

        try:
            sorted_nodes = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            raise RuntimeError(
                "TopologicalIntegrityError: DAG Certification bypassed; cycle detected during topological sort."
            )

        micro_tier_size = 10000
        current_batch = 0

        for node_id in sorted_nodes:
            self._calculate_localized_blast_radius(node_id)
            self._calculate_normalized_cvi_score(node_id)

            self._nodes_processed += 1
            current_batch += 1

            if current_batch >= micro_tier_size:
                await self._calibrate_traversal_pacing()
                self._push_hud_telemetry()
                current_batch = 0

        self._verify_cvi_activation_bounds()

    def _calculate_localized_blast_radius(self, node_id: Any) -> None:
        """
        Calculates Attenuated Kinetic Impact $I_{v}$ utilizing $L_1$ Norm summation of parent payloads.
        """
        base_threat = self.graph.nodes[node_id].get("base_threat_score", 1.0)
        accumulated_threat = base_threat

        # In a directed dependency graph, 'predecessors' are the packages that this node depends on.
        # Wait, if vulnerability flows DOWNSTREAM, it flows from dependency to dependent.
        # So we aggregate threat from PREDECESSORS to SUCCESSORS.
        for parent_id in self.graph.predecessors(node_id):
            parent_blast = self.graph.nodes[parent_id].get("blast_radius", 0.0)
            if parent_blast > 0.01:  # Critical-Mass Cutoff Pruning
                accumulated_threat += parent_blast * (1.0 - self._attenuation_gamma)

        self.graph.nodes[node_id]["blast_radius"] = accumulated_threat

    def _calculate_normalized_cvi_score(self, node_id: Any) -> None:
        """
        Sigmoid Fusion Manifold: Fuses hyper-dimensional telemetry into bounded $[0.00, 100.00]$ format.
        Prevents Telemetry Eclipse via Base-10 Logarithmic Financial Compression.
        """
        attrs = self.graph.nodes[node_id]

        c_val = attrs.get("eigen_centrality", 0.0) * 10000.0  # Scale up microscopic floats
        b_val = attrs.get("blast_radius", 0.0)

        f_raw = max(0.0, float(attrs.get("budget", 0.0)))
        f_val = math.log10(f_raw + 1.0)  # Logarithmic Compression

        m_raw = max(0.0, float(attrs.get("maintainers", 1.0)))
        m_val = 10.0 if m_raw == 0 else (1.0 / m_raw)  # Maintainer Deficit Risk

        # Linear Combination
        z = (
            (self._w_centrality * c_val)
            + (self._w_blast * b_val)
            + (self._w_finance * f_val)
            + (self._w_risk * m_val)
        )

        # Offset to center the sigmoid curve
        z_shifted = z - 2.0

        # Logistic Sigmoid Activation
        try:
            sigmoid_val = 1.0 / (1.0 + math.exp(-z_shifted))
        except OverflowError:
            sigmoid_val = 1.0 if z_shifted > 0 else 0.0

        cvi_score = round(sigmoid_val * 100.0, 2)

        attrs["cvi_score"] = cvi_score
        if cvi_score > self._max_cvi_observed:
            self._max_cvi_observed = cvi_score

    async def _calibrate_traversal_pacing(self) -> None:
        """
        Hardware-Aware Kinetic Gear-Box: Defends OS thermal/memory envelope utilizing GC-Pacing.
        """
        if not self.process_ref:
            return

        rss = self.process_ref.memory_info().rss
        if not self.is_redline or rss > (self._mem_limit_bytes * 0.8):
            gc.collect()
            await asyncio.sleep(0.005)
        else:
            await asyncio.sleep(0.001)

    def _push_hud_telemetry(self) -> Dict[str, Any]:
        """
        Kinetic-to-HUD Sync Manifold: Triggers the Double-Buffered Threat State for Detonation Ripples.
        """
        elapsed = max(0.001, time.monotonic() - self._start_time)
        velocity = self._nodes_processed / elapsed

        total_nodes = self.graph.number_of_nodes()
        depth_pct = min(100.0, (self._nodes_processed / max(1, total_nodes)) * 100.0)

        return {
            "WavefrontDepthPct": round(depth_pct, 2),
            "MaxCVIObserved": self._max_cvi_observed,
            "NodesProcessedPerSecond": round(velocity, 2),
            "TopologicalFrictionIndex": self._attenuation_gamma,
        }

    def _verify_cvi_activation_bounds(self) -> None:
        """
        Absolute Verdict Handoff Verification: Scans all calculated CVI scores for NaN/Inf/Out-of-Bounds.
        """
        cvi_scores = [attrs.get("cvi_score", 0.0) for _, attrs in self.graph.nodes(data=True)]
        if not cvi_scores:
            return

        cvi_array = np.array(cvi_scores, dtype=np.float64)

        if np.isnan(cvi_array).any() or np.isinf(cvi_array).any():
            raise RuntimeError(
                "MathematicalIntegrityError: NaN or Inf detected in final CVI scores."
            )

        cvi_min = np.min(cvi_array)
        cvi_max = np.max(cvi_array)

        if cvi_min < 0.0 or cvi_max > 100.0:
            raise RuntimeError(
                f"MathematicalIntegrityError: Sigmoid bounds breached. Range: [{cvi_min}, {cvi_max}]"
            )

        self.graph.graph["analytics_complete"] = True

    def yield_finalized_graph(self) -> nx.DiGraph:
        """Wait-Free Materialization Bus passing fully indexed DiGraph to serialization engines."""
        gc.collect()
        return self.graph
