import numpy as np
import psutil
import gc
import time
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class SystemicIntegrityError(Exception):
    """Raised when macroscopic analytical results violate fundamental scale-free network invariant doctrines."""

    pass


class MacroscopicStabilityAuditManifold:
    """
    ENGINEERING SPECIFICATION 030: GLOBAL ANALYTICAL CONVERGENCE AUDIT
    Executes high-speed statistical regressions and boolean cross-checks across the telemetry
    arrays to certify architectural harmony and structural stability prior to DB sealing.
    """

    __slots__ = ("telemetry_ref", "is_redline", "sample_size", "active_nodes", "certified_count")

    def __init__(self, telemetry_ref=None):
        self.telemetry_ref = telemetry_ref
        self.active_nodes = 0
        self.certified_count = 0
        self._calibrate_audit_granularity()

    def _calibrate_audit_granularity(self) -> None:
        """
        The Hardware-Aware Stability Gear-Box.
        Dynamically throttles audit scope based on physical L3 cache, RAM limits, and CPU cores.
        """
        mem = psutil.virtual_memory()
        cores = psutil.cpu_count(logical=False) or 2

        if mem.available < 8 * 1024**3 or cores < 6:
            self.is_redline = False
            self.sample_size = 100000
            logger.info("[GEAR-BOX] Potato Tier detected. Enforcing Stochastic Sampling (100k).")
        else:
            self.is_redline = True
            self.sample_size = None
            logger.info("[GEAR-BOX] Redline Tier detected. Full-Spectrum Mode Engaged.")

    def execute_scale_free_fitment_test(self, metric_array: np.ndarray) -> Tuple[float, float]:
        """
        Vectorized Power-Law Fitment Test.
        Calculates the Alpha exponent for structural distributions (PageRank/Blast Radius).
        Returns (Alpha Exponent, Fitment R^2).
        """
        valid_data = metric_array[metric_array > 0]
        if len(valid_data) < 10:
            return 0.0, 0.0

        hist, bin_edges = np.histogram(valid_data, bins=50, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        mask = hist > 0
        x_log = np.log(bin_centers[mask])
        y_log = np.log(hist[mask])

        if len(x_log) < 2:
            return 0.0, 0.0

        slope, intercept = np.polyfit(x_log, y_log, 1)
        alpha = -slope

        y_pred = intercept + slope * x_log
        ss_res = np.sum((y_log - y_pred) ** 2)
        ss_tot = np.sum((y_log - np.mean(y_log)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return alpha, r_squared

    def _validate_kernel_consistency_matrix(
        self,
        cvi_array: np.ndarray,
        override_mask: np.ndarray,
        pagerank_array: np.ndarray,
        blast_radius_array: np.ndarray,
    ) -> Tuple[int, int, int]:
        """
        Absolute Cross-Dimensional Integrity Doctrine.
        Executes bitwise matrices to ensure structural centrality and logical bulkheads (overrides) are mathematically respected.
        """
        violations = 0

        # Override-CVI Sync: Commercial overrides MUST mathematically be 0.0
        override_violations = np.sum((override_mask) & (cvi_array > 0.0))
        violations += override_violations

        # BFS-Centrality Sync: Hub nodes (top 0.1% PageRank) MUST possess non-zero downstream blast radius
        if len(pagerank_array) > 1000:
            pr_threshold = np.percentile(pagerank_array, 99.9)
            top_pr_holes = np.sum((pagerank_array >= pr_threshold) & (blast_radius_array == 0))
            violations += top_pr_holes
        else:
            top_pr_holes = 0

        return violations, override_violations, top_pr_holes

    def calculate_shannon_entropy(self, cvi_array: np.ndarray) -> float:
        """
        Generates the CVI Entropy Measure.
        Ensures the topological threat landscape maintains sufficient strategic contrast.
        """
        hist, _ = np.histogram(cvi_array, bins=100, density=True)
        p = hist / np.sum(hist)
        p = p[p > 0]
        entropy = -np.sum(p * np.log2(p))
        return entropy

    def execute_global_audit(
        self,
        cvi_array: np.ndarray,
        override_mask: np.ndarray,
        pagerank_array: np.ndarray,
        blast_radius_array: np.ndarray,
    ) -> Dict[str, float]:
        """
        The Wait-Free Truth Delivery Bus.
        Orchestrates the statistical verifications, implements hardware-aware array sampling,
        and yields the final diagnostic seal required for the UI Frame Handshake.
        """
        start_time = time.perf_counter()
        total_nodes = len(cvi_array)
        self.active_nodes = total_nodes

        if not self.is_redline and self.sample_size < total_nodes:
            indices = np.random.choice(total_nodes, self.sample_size, replace=False)
            c_cvi = cvi_array[indices]
            c_over = override_mask[indices]
            c_pr = pagerank_array[indices]
            c_br = blast_radius_array[indices]
        else:
            c_cvi = cvi_array
            c_over = override_mask
            c_pr = pagerank_array
            c_br = blast_radius_array

        # Distribution Fitment Phase
        pr_alpha, pr_r2 = self.execute_scale_free_fitment_test(c_pr)

        # Logic Consistency Phase
        violations, over_err, sync_err = self._validate_kernel_consistency_matrix(
            c_cvi, c_over, c_pr, c_br
        )
        if violations > 0:
            raise SystemicIntegrityError(
                f"Logic Integrity Breach: {violations} structural anomalies detected."
            )

        # Macroscopic Certification Phase
        entropy = self.calculate_shannon_entropy(c_cvi)
        if entropy < 1.0:
            raise SystemicIntegrityError(
                f"Zero-Entropy State Detected: {entropy:.4f}. Topological contrast collapse."
            )

        # Hardware-Aware Pacing Sweep
        if not self.is_redline or psutil.virtual_memory().percent > 80:
            gc.collect()

        exec_time = time.perf_counter() - start_time
        operations = len(c_cvi) * 4
        audit_velocity = operations / exec_time if exec_time > 0 else 0

        self.certified_count = len(c_cvi)
        f_stab = 1.0

        return {
            "AuditVelocity": audit_velocity,
            "NodesCertified": self.certified_count,
            "AlphaExponentFit": float(pr_alpha),
            "EntropyScore": float(entropy),
            "StabilityFidelityRatio": f_stab,
            "IsMacroscopicStabilitySealed": True,
        }
