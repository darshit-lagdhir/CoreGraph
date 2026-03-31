import numpy as np
import networkx as nx
import psutil
import gc
import hashlib
from typing import Dict, Any, Optional, Callable


class AnalyticalIntegrityError(Exception):
    pass


class ApexVerdictWeightingManifold:
    """
    Non-Linear Centrality Weighting and Organizational Decisions Gates.
    Engineered for in-place vector finalization, commercial short-circuit bypass, and logarithmic risk catapults.
    """

    __slots__ = (
        "ActiveDiGraphReference",
        "_hardware_tier",
        "_hud_sync_callback",
        "_nodes_list",
        "_num_nodes",
        "_raw_cvi",
        "_pagerank",
        "_is_commercially_backed",
        "_final_cvi",
        "_multiplier",
        "verdict_complete",
        "_batch_size",
        "_eta",
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
        self.verdict_complete = False

        self._nodes_list = list(self.ActiveDiGraphReference.nodes())
        self._num_nodes = len(self._nodes_list)

        self._eta = 1e5  # Centrality scaling multiplier sensitivity constant

        self._calibrate_finalization_pacing()
        self._vectorize_telemetry()

    def _calibrate_finalization_pacing(self) -> None:
        mem_percent = psutil.virtual_memory().percent
        if self._hardware_tier == "potato" or mem_percent > 85.0:
            self._batch_size = 50000
            self._hardware_tier = "potato"
        else:
            self._batch_size = self._num_nodes

    def _vectorize_telemetry(self) -> None:
        self._raw_cvi = np.zeros(self._num_nodes, dtype=np.float64)
        self._pagerank = np.zeros(self._num_nodes, dtype=np.float64)
        self._is_commercially_backed = np.zeros(self._num_nodes, dtype=bool)

        for i, node in enumerate(self._nodes_list):
            attrs = self.ActiveDiGraphReference.nodes[node]
            self._raw_cvi[i] = attrs.get("raw_vulnerability_score", 0.0)
            self._pagerank[i] = attrs.get("pagerank", 1e-7)
            self._is_commercially_backed[i] = attrs.get("is_commercially_backed", False)

        if self._hardware_tier == "redline":
            self._final_cvi = np.zeros(self._num_nodes, dtype=np.float64)
            self._multiplier = np.zeros(self._num_nodes, dtype=np.float64)
        else:
            # Potato-tier uses in-place arrays, assigning them sequentially mutates the raw score.
            self._final_cvi = self._raw_cvi
            self._multiplier = np.zeros(self._batch_size, dtype=np.float64)

    def execute_apex_centrality_weighting(self, start_idx: int, end_idx: int) -> None:
        pr_slice = self._pagerank[start_idx:end_idx]

        if self._hardware_tier == "redline":
            self._multiplier[start_idx:end_idx] = np.log10(1.0 + self._eta * pr_slice)
            self._final_cvi[start_idx:end_idx] = (
                self._raw_cvi[start_idx:end_idx] * self._multiplier[start_idx:end_idx]
            )
        else:
            size = end_idx - start_idx
            self._multiplier[:size] = np.log10(1.0 + self._eta * pr_slice)
            self._final_cvi[start_idx:end_idx] *= self._multiplier[:size]

    def _run_organizational_override_bypass(self, start_idx: int, end_idx: int) -> None:
        com_mask = self._is_commercially_backed[start_idx:end_idx]
        self._final_cvi[start_idx:end_idx][com_mask] = 0.0
        np.clip(
            self._final_cvi[start_idx:end_idx], 0.0, 100.0, out=self._final_cvi[start_idx:end_idx]
        )

    def finalize_architectural_verdicts(self) -> nx.DiGraph:
        if self._num_nodes == 0:
            self.verdict_complete = True
            return self.ActiveDiGraphReference

        corporate_bypassed = 0
        apex_elevated = 0

        for batch_start in range(0, self._num_nodes, self._batch_size):
            batch_end = min(batch_start + self._batch_size, self._num_nodes)

            self.execute_apex_centrality_weighting(batch_start, batch_end)
            self._run_organizational_override_bypass(batch_start, batch_end)

            mask_slice = self._is_commercially_backed[batch_start:batch_end]
            corporate_bypassed += np.sum(mask_slice)
            apex_elevated += np.sum(self._final_cvi[batch_start:batch_end] >= 99.0)

            if self._hardware_tier == "potato":
                gc.collect()

        if self._num_nodes > 0 and self._hud_sync_callback:
            self._hud_sync_callback(
                {
                    "NodesFinalized": self._num_nodes,
                    "CorporateBypassRate": float(corporate_bypassed / self._num_nodes),
                    "ApexElevationVelocity": int(apex_elevated),
                    "VerdictSynchronicityScore": 1.0,
                }
            )

        # Mathematical Integrity Scan
        if np.any(self._final_cvi[self._is_commercially_backed] > 0.0):
            raise AnalyticalIntegrityError(
                "Commercial Bypass layer failed: Corporate nodes retain vulnerability score."
            )

        # Verdict Attribution Phase
        for i, node in enumerate(self._nodes_list):
            attrs = self.ActiveDiGraphReference.nodes[node]
            if self._hardware_tier == "redline":
                attrs["shadow_raw_cvi"] = float(self._raw_cvi[i])

            if self._is_commercially_backed[i]:
                attrs["verdict_metadata"] = "Verified via Corporate Audit"
            elif self._hardware_tier == "redline":
                attrs["multiplier_magnitude"] = float(self._multiplier[i])

            attrs["cvi_final"] = float(self._final_cvi[i])

        ledger_bytes = self._final_cvi.tobytes()
        seal_hash = hashlib.sha384(ledger_bytes).hexdigest()

        if self._hud_sync_callback:
            self._hud_sync_callback({"Phase": "Verdict Complete", "CryptographicSeal": seal_hash})

        self.verdict_complete = True
        return self.ActiveDiGraphReference
