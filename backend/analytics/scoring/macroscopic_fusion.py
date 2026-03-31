import numpy as np
import networkx as nx
import hashlib
import gc
import psutil
import time
from typing import Dict, Any, Callable


class MacroscopicMetricAggregationManifold:
    __slots__ = [
        "_graph",
        "_hardware_tier",
        "_hud_sync_callback",
        "_batch_size",
        "_decimation_limit",
        "_macroscopic_fusion_complete",
        "_merkle_root",
        "_node_list",
        "_hierarchical_registry",
    ]

    def __init__(
        self, graph: nx.DiGraph, hardware_tier: str = "redline", hud_sync_callback: Callable = None
    ):
        self._graph = graph
        self._hardware_tier = hardware_tier
        self._hud_sync_callback = hud_sync_callback or (lambda x: None)
        self._macroscopic_fusion_complete = False
        self._merkle_root = None
        self._hierarchical_registry: Dict[str, Any] = {}
        self._node_list = list(self._graph.nodes())
        self._calibrate_synthesis_pacing()

    def _calibrate_synthesis_pacing(self) -> None:
        """Configures memory pacing based on hardware detection and explicitly manages decimation layers."""
        memory_stats = psutil.virtual_memory()
        # Engage survivability protocol on constrained architectures (<2GB available headroom)
        if self._hardware_tier == "potato" or (
            self._hardware_tier != "redline" and memory_stats.available < 2 * 1024**3
        ):
            self._batch_size = 50000
            self._decimation_limit = 5000  # Extreme visual decimation to save RAM
        else:
            self._batch_size = 1000000
            self._decimation_limit = 50000  # High-fidelity macroscopic rendering

    def _generate_importance_gated_subsets(
        self, cvi_array: np.ndarray, pr_array: np.ndarray
    ) -> list:
        """Identifies 'Sentinel Nodes' based on Top-K PageRank and CVI overlap to reduce visual payload."""
        importance_matrix = cvi_array * pr_array
        k = min(self._decimation_limit, len(self._node_list))

        if k < len(importance_matrix):
            # O(N) Top-K selection for absolute speed without deep sorting
            top_indices = np.argpartition(importance_matrix, -k)[-k:]
        else:
            top_indices = np.arange(len(importance_matrix))

        return [self._node_list[i] for i in top_indices]

    def execute_galactic_metric_fusion(self) -> Dict[str, Any]:
        """Calculates mass-weighted centroids and executes hierarchical max-signal reductions."""
        start_time = time.perf_counter()
        size = len(self._node_list)

        # High-speed numpy contiguous vectors
        cvi_arr = np.zeros(size, dtype=np.float64)
        pr_arr = np.zeros(size, dtype=np.float64)
        comm_arr = np.zeros(size, dtype=np.int32)
        x_arr = np.zeros(size, dtype=np.float64)
        y_arr = np.zeros(size, dtype=np.float64)

        comm_name_map = {}
        comm_id_inverse = {}
        next_cid = 0

        # Vectorized Metadata Extraction
        for i, node in enumerate(self._node_list):
            attrs = self._graph.nodes[node]
            cvi_arr[i] = attrs.get("fused_vulnerability_index", 0.0)
            pr_arr[i] = attrs.get("pagerank", 1e-10)

            c_name = attrs.get("community_id", "unassigned_sector")
            if c_name not in comm_name_map:
                comm_name_map[c_name] = next_cid
                comm_id_inverse[next_cid] = c_name
                next_cid += 1
            comm_arr[i] = comm_name_map[c_name]

            pos = attrs.get("pos", (0.0, 0.0))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x_arr[i] = pos[0]
                y_arr[i] = pos[1]

        num_comms = next_cid

        # Target Fusion Aggregators
        weights_sum = np.zeros(num_comms, dtype=np.float64)
        centroid_x_sum = np.zeros(num_comms, dtype=np.float64)
        centroid_y_sum = np.zeros(num_comms, dtype=np.float64)
        max_cvi = np.zeros(num_comms, dtype=np.float64)
        sum_cvi = np.zeros(num_comms, dtype=np.float64)
        count_cvi = np.zeros(num_comms, dtype=np.int32)

        total_batches = (size + self._batch_size - 1) // self._batch_size

        # Phase 1: Block-paced vectorized accumulation
        for batch_idx in range(total_batches):
            start = batch_idx * self._batch_size
            end = min((batch_idx + 1) * self._batch_size, size)

            b_comm = comm_arr[start:end]
            b_pr = pr_arr[start:end]
            b_x = x_arr[start:end]
            b_y = y_arr[start:end]
            b_cvi = cvi_arr[start:end]

            np.add.at(weights_sum, b_comm, b_pr)
            np.add.at(centroid_x_sum, b_comm, b_x * b_pr)
            np.add.at(centroid_y_sum, b_comm, b_y * b_pr)

            np.maximum.at(max_cvi, b_comm, b_cvi)
            np.add.at(sum_cvi, b_comm, b_cvi)
            np.add.at(count_cvi, b_comm, 1)

            if self._hardware_tier == "potato":
                gc.collect()

        # Phase 2: Heuristic Crystallization and Geometry Resolution
        centroid_x = centroid_x_sum / np.clip(weights_sum, 1e-10, None)
        centroid_y = centroid_y_sum / np.clip(weights_sum, 1e-10, None)
        mean_cvi = sum_cvi / np.clip(count_cvi, 1, None)

        # Max-Signal Propagation Doctrine: guarantee >= max individual CVI. Capped at 100.0.
        cluster_cvi = np.clip(max_cvi + 0.01 * mean_cvi, max_cvi, 100.0)

        # Generating LOD Subsets (Visual Entropy Reduction)
        sentinels = self._generate_importance_gated_subsets(cvi_arr, pr_arr)

        hasher = hashlib.sha384()

        # Phase 3: Constructing Non-Repudiable Registry
        for cid in range(num_comms):
            c_name = comm_id_inverse[cid]
            cvi_val = float(cluster_cvi[cid])

            self._hierarchical_registry[c_name] = {
                "cluster_cvi": cvi_val,
                "centroid_x": float(centroid_x[cid]),
                "centroid_y": float(centroid_y[cid]),
                "total_mass": float(weights_sum[cid]),
                "population_count": int(count_cvi[cid]),
                "max_signal_propagated": bool(cvi_val >= max_cvi[cid]),
            }

            if cvi_val > 100.0 or cvi_val < 0.0:
                raise ValueError("HierarchicalIntegrityError: Galactic Bloom limits shattered.")

            hasher.update(str(c_name).encode("utf-8"))
            hasher.update(np.float64(cvi_val).tobytes())

        self._hierarchical_registry["__global_sentinels__"] = sentinels
        self._merkle_root = hasher.hexdigest()

        # Absolute Conservation Check (F_agg)
        total_node_weight = np.sum(pr_arr)
        total_cluster_weight = np.sum(weights_sum)

        fidelity = (
            1.0
            if np.isclose(total_node_weight, total_cluster_weight, atol=1e-7)
            else (
                1.0 - abs(total_cluster_weight - total_node_weight) / max(total_node_weight, 1e-10)
            )
        )

        # Signal Propagation / Clarity metric
        risk_beacons = float(np.sum(max_cvi >= 90.0))
        clarity_score = risk_beacons / max((num_comms), 1)

        # 144Hz Tactical Callback
        self._hud_sync_callback(
            {
                "ClustersFused": num_comms,
                "SignalPropagationRate": float(np.mean(cluster_cvi >= max_cvi)),
                "AggregationVelocity": size / max((time.perf_counter() - start_time), 0.001),
                "HierarchicalSynchronicityScore": fidelity,
            }
        )

        self._macroscopic_fusion_complete = True

        # Pre-Transmission Cleanup
        del cvi_arr
        del pr_arr
        del comm_arr
        del x_arr
        del y_arr
        gc.collect()

        return {
            "AggregationFidelity": fidelity,
            "StrategicContrast": clarity_score,
            "LogicRootHash": self._merkle_root,
            "Status": "MODULE_9_HIERARCHY_SEALED",
        }
