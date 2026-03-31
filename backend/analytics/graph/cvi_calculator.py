import numpy as np
import networkx as nx
import psutil
import gc
import time
import hashlib
from typing import Dict, Any, Optional, Callable


class TopologicalMathematicalError(Exception):
    pass


class CompositeVulnerabilityFusionManifold:
    """
    Non-Linear Risk Fusion Kernel & Composite Vulnerability Index (CVI) Normalization Engine.
    Engineered for SIMD vectorization, Logarithmic Deficit Scaling, and Exponential Decay Logic.
    """

    __slots__ = (
        "ActiveDiGraphReference",
        "_hardware_tier",
        "_hud_sync_callback",
        "_batch_size",
        "_nodes_list",
        "_num_nodes",
        "_pagerank",
        "_usd",
        "_maintainers",
        "_latency",
        "_cvi",
        "_financial_deficit",
        "_human_burnout",
        "_weights",
        "cvi_fusion_complete",
    )

    def __init__(
        self,
        target_graph: nx.DiGraph,
        hardware_tier: str = "redline",
        hud_sync_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.ActiveDiGraphReference = target_graph
        self._hardware_tier = hardware_tier
        self._hud_sync_callback = hud_sync_callback
        self.cvi_fusion_complete = False

        self._nodes_list = list(self.ActiveDiGraphReference.nodes())
        self._num_nodes = len(self._nodes_list)

        self._pagerank = np.zeros(self._num_nodes, dtype=np.float64)
        self._usd = np.zeros(self._num_nodes, dtype=np.float64)
        self._maintainers = np.zeros(self._num_nodes, dtype=np.float64)
        self._latency = np.zeros(self._num_nodes, dtype=np.float64)

        self._cvi = np.zeros(self._num_nodes, dtype=np.float64)
        self._financial_deficit = np.zeros(self._num_nodes, dtype=np.float64)
        self._human_burnout = np.zeros(self._num_nodes, dtype=np.float64)

        self._weights = {"finance": 0.35, "human": 0.45, "struct": 0.20}

        self._calibrate_scoring_pacing()
        self._vectorize_telemetry()

    def _calibrate_scoring_pacing(self) -> None:
        """
        Calculates Resident Set Size limits to determine array slicing velocity.
        """
        mem_percent = psutil.virtual_memory().percent
        if self._hardware_tier == "potato" or mem_percent > 85.0:
            self._batch_size = 50000
            self._hardware_tier = "potato"
        else:
            self._batch_size = self._num_nodes

    def _vectorize_telemetry(self) -> None:
        """
        Extracts native NetworkX graph attributes into contiguous cache-aligned NumPy FPU blocks.
        """
        current_time = time.time()
        for i, node in enumerate(self._nodes_list):
            attrs = self.ActiveDiGraphReference.nodes[node]
            self._pagerank[i] = attrs.get("pagerank", 1e-7)
            self._usd[i] = attrs.get("usd_balance", 0.0)
            self._maintainers[i] = max(1.0, float(attrs.get("maintainer_count", 1.0)))

            last_commit = attrs.get("last_commit_timestamp", current_time)
            delta_days = (current_time - last_commit) / 86400.0
            self._latency[i] = max(0.0, delta_days)

    def execute_financial_normalization(self, start_idx: int, end_idx: int) -> None:
        """
        Calculates scale-disparity neutral balances through extreme logarithmic compression.
        """
        pr_slice = self._pagerank[start_idx:end_idx]
        usd_slice = self._usd[start_idx:end_idx]

        baseline_requirement = pr_slice * 1_000_000.0
        deficit = np.maximum(0.0, baseline_requirement - usd_slice)

        self._financial_deficit[start_idx:end_idx] = np.log10(deficit + 1.0) * 10.0

    def _calculate_maintainer_burnout_decay(self, start_idx: int, end_idx: int) -> None:
        """
        Calculates exponential latency drops relative to current maintainer capacity constraints.
        """
        lat_slice = self._latency[start_idx:end_idx]
        maint_slice = self._maintainers[start_idx:end_idx]

        base_decay = np.power(1.005, lat_slice)
        scarcity_multi = 1.0 / np.maximum(1.0, maint_slice)

        burnout = base_decay * scarcity_multi * 10.0
        self._human_burnout[start_idx:end_idx] = np.minimum(100.0, burnout)

    def execute_fusion_synthesis(self) -> nx.DiGraph:
        """
        Master execution loop bridging structural analysis with predictive mathematical rendering.
        """
        if self._num_nodes == 0:
            self.cvi_fusion_complete = True
            return self.ActiveDiGraphReference

        t_start = time.perf_counter()

        for batch_start in range(0, self._num_nodes, self._batch_size):
            batch_end = min(batch_start + self._batch_size, self._num_nodes)

            self.execute_financial_normalization(batch_start, batch_end)
            self._calculate_maintainer_burnout_decay(batch_start, batch_end)

            fin_slice = self._financial_deficit[batch_start:batch_end]
            hum_slice = self._human_burnout[batch_start:batch_end]
            struc_slice = np.log10(self._pagerank[batch_start:batch_end] * 1e6 + 1.0) * 20.0

            raw_cvi = (
                (fin_slice * self._weights["finance"])
                + (hum_slice * self._weights["human"])
                + (struc_slice * self._weights["struct"])
            )

            # Logistic Sigmoid bounding the output to absolute [0, 100] range
            clamped_cvi = 100.0 / (1.0 + np.exp(-0.15 * (raw_cvi - 40.0)))

            # Zero-Trust fallback
            invalid_mask = np.isnan(clamped_cvi) | np.isinf(clamped_cvi)
            clamped_cvi[invalid_mask] = 100.0

            self._cvi[batch_start:batch_end] = np.clip(np.round(clamped_cvi, 2), 0.0, 100.0)

            if self._hardware_tier == "potato":
                gc.collect()

            if self._hud_sync_callback:
                t_delta = max((time.perf_counter() - t_start), 0.0001)
                self._hud_sync_callback(
                    {
                        "NodesFused": batch_end,
                        "CVI_Velocity": batch_end / t_delta,
                        "DeficitSaturationRate": float(np.mean(fin_slice) / 100.0),
                        "BoundaryAdherenceScore": 1.0,
                    }
                )

        # Pre-Multiplier Sanitation Protocol
        invalid_final_mask = np.isnan(self._cvi) | np.isinf(self._cvi)
        if np.any(invalid_final_mask):
            raise TopologicalMathematicalError(
                "Boundary Breach: Sigmoid layer collapsed with NaN or Inf values."
            )

        for i, node in enumerate(self._nodes_list):
            self.ActiveDiGraphReference.nodes[node]["raw_vulnerability_score"] = self._cvi[i]

        ledger_bytes = self._cvi.tobytes()
        fusion_hash = hashlib.sha384(ledger_bytes).hexdigest()

        if self._hud_sync_callback:
            self._hud_sync_callback({"Phase": "Fusion Complete", "CryptographicSeal": fusion_hash})

        self.cvi_fusion_complete = True
        return self.ActiveDiGraphReference
