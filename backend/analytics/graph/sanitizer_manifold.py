import asyncio
import gc
import hashlib
import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any, Set, Tuple

try:
    import psutil
except ImportError:
    psutil = None

import networkx as nx


def _parallel_scc_evaluator(
    scc_edges: List[Tuple[Any, Any, Dict[str, Any]]], alpha: float, beta: float
) -> Tuple[Any, Any]:
    """
    Module-level pure function for Quantum Eradication Mode multiprocess mapping.
    Avoids pickling the massive global DiGraph by operating on isolated edge data.
    """
    highest_score = -float("inf")
    highest_hash = -1
    target_edge = None

    for u, v, u_data in scc_edges:
        out_degree = u_data.get("out_degree", 1)
        deprecation_val = u_data.get("deprecation", 0.0)

        # Primary Heuristic: D_{out} and Deprecation Penalty
        score = (alpha * (1.0 / max(1, out_degree))) + (beta * deprecation_val)

        # Isolation Penalty Multiplier
        if u_data.get("in_degree", 1) <= 1:
            score *= 0.1  # Heavy isolation penalty to prevent orphaning

        u_str, v_str = str(u), str(v)
        tie_breaker_hash = int(hashlib.sha256(f"{u_str}{v_str}".encode()).hexdigest(), 16)

        if score > highest_score or (score == highest_score and tie_breaker_hash > highest_hash):
            highest_score = score
            highest_hash = tie_breaker_hash
            target_edge = (u, v)

    if target_edge is None:
        raise ValueError("No viable edge found for decimation.")

    return target_edge


class DeterministicTopologicalSanitizer:
    """
    The Deterministic Topological Sanitizer and Depth-First Cycle Resolution Kernel.
    Mathematical Purifier enforcing Absolute Deterministic Heuristic Severance.
    """

    __slots__ = (
        "graph",
        "is_redline",
        "process_ref",
        "_start_time",
        "_cycles_resolved",
        "_edges_severed",
        "_hashes_executed",
        "_initial_cycles",
        "_mem_limit_bytes",
        "_alpha",
        "_beta",
    )

    def __init__(self, graph: nx.DiGraph, is_redline: bool = True):
        self.graph = graph
        self.is_redline = is_redline
        self.process_ref = psutil.Process(os.getpid()) if psutil else None
        self._start_time = time.monotonic()
        self._cycles_resolved = 0
        self._edges_severed = 0
        self._hashes_executed = 0
        self._initial_cycles = -1
        self._mem_limit_bytes = 150 * 1024 * 1024  # 150MB constraint
        self._alpha = 1.0
        self._beta = 1.0

    async def execute_sanitization_pipeline(self) -> nx.DiGraph:
        """
        Wait-Free Certified Delivery Bus: Oversees the iterative Tarjan sweep and surgical resolution.
        """
        while not nx.is_directed_acyclic_graph(self.graph):
            scc_list = self.identify_strongly_connected_components()

            if self._initial_cycles == -1:
                self._initial_cycles = len(scc_list)

            if self.is_redline:
                await self._execute_quantum_eradication(scc_list)
            else:
                await self._execute_survivability_eradication(scc_list)

            self._push_hud_telemetry()
            await asyncio.sleep(0.01)  # Frame-Aligned Eradication Coalescing

        self.graph.graph["is_dag_certified"] = True
        return self.yield_certified_dag()

    def identify_strongly_connected_components(self) -> List[Set[Any]]:
        """
        Iterative Tarjan SCC Kernel: Recursion-Safe Discovery utilizing non-recursive stack loops.
        """
        # NetworkX relies on a highly optimized iterative stack for strongly_connected_components
        return [scc for scc in nx.strongly_connected_components(self.graph) if len(scc) > 1]

    def _extract_cycle_edge_data(self, u: Any, v: Any) -> Tuple[Any, Any, Dict[str, Any]]:
        """Extracts required node-state metrics for isolated weight calculation."""
        u_data = {
            "out_degree": self.graph.out_degree(u),
            "in_degree": self.graph.in_degree(u),
            "deprecation": self.graph.nodes[u].get("deprecation", 0.0),
        }
        return (u, v, u_data)

    def _calculate_edge_severance_weight(self, u: Any, v: Any) -> Tuple[float, int]:
        """
        Deterministic Heuristic Manifold: Applies mathematical weights and SHA-256 fallbacks.
        """
        out_degree = self.graph.out_degree(u)
        deprecation_val = self.graph.nodes[u].get("deprecation", 0.0)
        in_degree = self.graph.in_degree(u)

        score = (self._alpha * (1.0 / max(1, out_degree))) + (self._beta * deprecation_val)

        # Reachability Validation / Isolation Penalty
        if in_degree <= 1:
            score *= 0.1

        u_str, v_str = str(u), str(v)
        tie_breaker_hash = int(hashlib.sha256(f"{u_str}{v_str}".encode()).hexdigest(), 16)
        self._hashes_executed += 1

        return score, tie_breaker_hash

    def _execute_surgical_snip(self, cycle_edges: List[Tuple[Any, Any]]) -> None:
        """
        Identifies highest liability score in the cycle and systematically removes the edge.
        """
        highest_score = -float("inf")
        highest_hash = -1
        target_edge = None

        for u, v in cycle_edges:
            score, t_hash = self._calculate_edge_severance_weight(u, v)
            if score > highest_score or (score == highest_score and t_hash > highest_hash):
                highest_score = score
                highest_hash = t_hash
                target_edge = (u, v)

        if target_edge and self.graph.has_edge(*target_edge):
            self.graph.remove_edge(*target_edge)
            self._edges_severed += 1

    async def _execute_quantum_eradication(self, scc_list: List[Set[Any]]) -> None:
        """
        Redline Tier: Highly parallel sub-graph edge weight resolution pool.
        """
        tasks = []
        for scc_nodes in scc_list:
            sub = self.graph.subgraph(scc_nodes)
            try:
                cycle_edges = list(nx.find_cycle(sub, orientation="original"))
                edge_payload = [self._extract_cycle_edge_data(u, v) for u, v in cycle_edges]
                tasks.append(edge_payload)
            except nx.NetworkXNoCycle:
                continue

        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            futures = [
                loop.run_in_executor(
                    pool, _parallel_scc_evaluator, p_edges, self._alpha, self._beta
                )
                for p_edges in tasks
            ]
            results = await asyncio.gather(*futures)

        for target_edge in results:
            if target_edge and self.graph.has_edge(*target_edge):
                self.graph.remove_edge(*target_edge)
                self._edges_severed += 1
                self._cycles_resolved += 1

    async def _execute_survivability_eradication(self, scc_list: List[Set[Any]]) -> None:
        """
        Potato Tier: Deterministic Sequential Purging and GC-Pacing.
        """
        batch_size = 100
        processed = 0

        for scc_nodes in scc_list:
            sub = self.graph.subgraph(scc_nodes)
            try:
                cycle_edges = list(nx.find_cycle(sub, orientation="original"))
                self._execute_surgical_snip(cycle_edges)
                self._cycles_resolved += 1
                processed += 1
            except nx.NetworkXNoCycle:
                continue

            if processed >= batch_size:
                self._invoke_gc_pacing()
                processed = 0
                await asyncio.sleep(0.001)

        self._invoke_gc_pacing()

    def _invoke_gc_pacing(self) -> None:
        """Forceful garbage collector sweeps to compact dictionary spaces."""
        if not self.process_ref:
            gc.collect()
            return

        rss = self.process_ref.memory_info().rss
        if rss > self._mem_limit_bytes:
            gc.collect()

    def _push_hud_telemetry(self) -> Dict[str, Any]:
        """
        Surgical-to-HUD Sync Manifold: Resolves telemetrics for Topological Purity Overlay.
        """
        elapsed = max(0.001, time.monotonic() - self._start_time)
        v_inst = self._edges_severed / elapsed

        q_acyclic = (
            1.0
            if self._initial_cycles <= 0
            else 1.0 - (max(0, self._initial_cycles - self._cycles_resolved) / self._initial_cycles)
        )

        v_det = self._hashes_executed / max(1, self._edges_severed)

        return {
            "CyclesResolved": self._cycles_resolved,
            "EdgesSevered": self._edges_severed,
            "ResolutionVelocity": round(v_inst, 2),
            "AcyclicityQuotient": round(q_acyclic, 4),
            "DeterminismVariance": round(v_det, 4),
            "DAGCertificationStatus": (
                "VERIFIED" if nx.is_directed_acyclic_graph(self.graph) else "UNVERIFIED"
            ),
        }

    def yield_certified_dag(self) -> nx.DiGraph:
        """Immutable Reference Passing and Pre-Analytics Garbage Collection."""
        gc.collect()
        return self.graph
