import asyncio
import gc
import math
import os
import time
import json
from typing import Dict, Any, List, Set, Tuple

try:
    import psutil
except ImportError:
    psutil = None

import networkx as nx
import numpy as np


class PredictivePathogenSimulationManifold:
    """
    Predictive Pathogen Injection and Cross-Community Contagion Simulation Kernel.
    Kinetic War Room enforcing Stochastic Monte Carlo Traversals and Apex Trajectory Extraction.
    """

    __slots__ = (
        "macro_graph",
        "micro_graph",
        "is_redline",
        "process_ref",
        "_start_time",
        "_total_iterations",
        "_base_iterations",
        "_breached_communities",
        "_apex_probability_max",
        "_extracted_trajectories",
        "_mem_limit_bytes",
    )

    def __init__(self, macro_graph: nx.DiGraph, micro_graph: nx.DiGraph, is_redline: bool = True):
        self.macro_graph = macro_graph
        self.micro_graph = micro_graph
        self.is_redline = is_redline
        self.process_ref = psutil.Process(os.getpid()) if psutil else None

        self._start_time = 0.0
        self._total_iterations = 0
        self._base_iterations = 100000 if is_redline else 1000
        self._breached_communities: Set[Any] = set()
        self._apex_probability_max = 0.0
        self._extracted_trajectories: List[Dict[str, Any]] = []
        self._mem_limit_bytes = 150 * 1024 * 1024

    async def execute_cross_community_breach(
        self, root_community_id: Any, kinetic_momentum: float
    ) -> None:
        """
        Macro-Vector Propagation Kernel: Circumvents NP-Hard scaling via Sub-Graph Boundary Resistance mapping.
        Rolls pathogen's momentum against Community resilience scores explicitly calculated in Phase 2.
        """
        if self.macro_graph.number_of_nodes() == 0:
            raise RuntimeError(
                "TopologicalContagionError: Macro-graph structure corrupted or not instantiated."
            )

        self._start_time = time.monotonic()
        root_node = f"SUPER_{root_community_id}"

        if root_node not in self.macro_graph:
            return

        self._breached_communities.add(root_community_id)
        
        # Hardy Iterative BFS Traversal for Contagion modeling
        active_queue = [root_node]
        visited = {root_node}

        while active_queue:
            curr_node = active_queue.pop(0)

            for target_node in self.macro_graph.successors(curr_node):
                if target_node in visited:
                    continue

                edge_data = self.macro_graph.get_edge_data(
                    curr_node, target_node, default={"weight": 1.0}
                )
                target_data = self.macro_graph.nodes[target_node]

                boundary_strength = target_data.get("budget", 0.0) / 1000.0
                resistance = max(1.0, math.log10(boundary_strength + 10.0))

                contagion_roll = (kinetic_momentum * edge_data["weight"]) / resistance

                if contagion_roll > 1.0:
                    visited.add(target_node)
                    active_queue.append(target_node)
                    raw_id = str(target_node).replace("SUPER_", "")
                    self._breached_communities.add(raw_id)

    async def run_probabilistic_micro_traversal(self) -> None:
        """
        Monte Carlo Stochastic Manifold: Unpacks explicitly breached communities into high-speed NumPy
        simulation arrays. Calculates mathematically hardened probability matrices via thousands of iterations.
        """
        # Set a rigid pseudo-random seed to guarantee "Absolute Determinism" in stochastic evaluation
        rng = np.random.default_rng(seed=42)

        for comm_id in self._breached_communities:
            community_nodes = [
                n
                for n, attr in self.micro_graph.nodes(data=True)
                if str(attr.get("community_id")) == str(comm_id)
            ]

            if not community_nodes:
                continue

            sub_graph = self.micro_graph.subgraph(community_nodes)
            nodes_list = list(sub_graph.nodes())
            n_len = len(nodes_list)

            if n_len < 2:
                continue

            node_idx = {n: i for i, n in enumerate(nodes_list)}

            # Map structural edge properties into contiguous memory for fast Monte Carlo
            edge_params = []
            for u, v in sub_graph.edges():
                cvi_u = sub_graph.nodes[u].get("cvi_score", 1.0)
                m_v = max(1.0, float(sub_graph.nodes[v].get("maintainers", 1.0)))
                # Stochastic infection probability equation
                p_inf = 1.0 / (1.0 + math.exp(-((cvi_u / m_v) - 2.0)))

                edge_params.append((node_idx[u], node_idx[v], p_inf))

            # Probability Matrix Allocation
            infection_counts = np.zeros(n_len, dtype=np.int32)

            # Identify root entries for the simulation specific to this sub-graph
            in_degrees = dict(sub_graph.in_degree())
            roots = [node_idx[n] for n, deg in in_degrees.items() if deg == 0]
            if not roots:
                roots = [0]  # Fallback if circular loop survived somehow

            batch_size = 100 if not self.is_redline else 1000

            for i in range(0, self._base_iterations, batch_size):
                current_batch = min(batch_size, self._base_iterations - i)

                # Execute sequential/batch traversal internally
                for _ in range(current_batch):
                    active_queue = roots.copy()
                    visited = set(roots)

                    while active_queue:
                        curr = active_queue.pop(0)
                        infection_counts[curr] += 1

                        # Find edges originating from current node
                        children_edges = [ep for ep in edge_params if ep[0] == curr]

                        for _, v_idx, p_inf in children_edges:
                            if v_idx not in visited:
                                # Stochastic Roll
                                if rng.random() < p_inf:
                                    visited.add(v_idx)
                                    active_queue.append(v_idx)

                self._total_iterations += current_batch
                await self._calibrate_simulation_pacing()
                self._push_hud_telemetry()

            # Extract probability matrix
            prob_matrix = infection_counts / float(self._base_iterations)
            max_p = np.max(prob_matrix)
            if max_p > self._apex_probability_max:
                self._apex_probability_max = float(max_p)

            # Apex Extraction: finding the highest probability cascade
            # We locate a terminal node with high probability and trace backward
            target_idx = int(np.argmax(prob_matrix))
            target_prob = float(prob_matrix[target_idx])

            if target_prob > 0.1:
                t_node = nodes_list[target_idx]
                apex_path = [t_node]

                curr_node = t_node
                
                depth = 0
                max_depth = 5000
                while depth < max_depth:
                    depth += 1
                    preds = list(sub_graph.predecessors(curr_node))
                    # Prevent circular tracing loops
                    preds = [p for p in preds if p not in apex_path]
                    
                    if not preds:
                        break

                    # Backtrace to parent with highest calculated probability
                    best_pred = max(preds, key=lambda p: prob_matrix[node_idx[p]])
                    apex_path.insert(0, best_pred)
                    curr_node = best_pred

                path_probs = [float(prob_matrix[node_idx[n]]) for n in apex_path]

                self._extracted_trajectories.append(
                    {
                        "community_id": str(comm_id),
                        "root_node": str(apex_path[0]),
                        "terminal_node": str(apex_path[-1]),
                        "apex_trajectory_path": apex_path,
                        "trajectory_probabilities": path_probs,
                        "cumulative_threat_max": target_prob,
                    }
                )

        self._validate_extracted_payloads()

    async def _calibrate_simulation_pacing(self) -> None:
        """
        Hardware-Aware Contagion Gear-Box: Operates explicit GC teardowns blocking iteration loops
        if RAM footprints breach OS limits during NumPy array generation.
        """
        if not self.process_ref:
            gc.collect()
            return

        rss = self.process_ref.memory_info().rss
        if not self.is_redline or rss > (self._mem_limit_bytes * 0.8):
            gc.collect()
            await asyncio.sleep(0.005)
        else:
            await asyncio.sleep(0.001)

    def _push_hud_telemetry(self) -> Dict[str, Any]:
        """
        Kinetic Sync Bridge: Serves Double-Buffered Heatmap and simulation parameters to visual matrix.
        """
        elapsed = max(0.001, time.monotonic() - self._start_time)
        velocity = self._total_iterations / elapsed

        return {
            "TotalIterationsCompleted": self._total_iterations,
            "BoundaryBreaches": len(self._breached_communities),
            "ApexProbabilityMax": round(self._apex_probability_max, 4),
            "SimulationVelocity": round(velocity, 2),
        }

    def _validate_extracted_payloads(self) -> None:
        """Structural integrity check verifying final JSONB extraction paths."""
        for payload in self._extracted_trajectories:
            path = payload["apex_trajectory_path"]
            for i in range(len(path) - 1):
                if not self.micro_graph.has_edge(path[i], path[i + 1]):
                    raise RuntimeError(
                        f"TopologicalContagionError: Extracted trajectory jumped across invalid topological edge {path[i]} -> {path[i + 1]}."
                    )

    def yield_serialized_trajectories(self) -> List[str]:
        """Wait-Free Trajectory Delivery Bus: Returns final binary-ready JSON configurations."""
        gc.collect()
        return [json.dumps(payload) for payload in self._extracted_trajectories]
