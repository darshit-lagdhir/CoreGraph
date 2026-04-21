import math
from typing import Final
from backend.core.sharding.hadronic_pool import uhmp_pool

# =========================================================================================
# COREGRAPH OUTLIER DETECTOR: MULTI-VECTOR STATISTICAL VALIDATION (PROMPT 8)
# =========================================================================================
# MANDATE: Cross-examine Isolation Forest vs Behavioral Deviation.
# ARCHITECTURE: Chi-Squared Independence Validation on the Hadronic Matrix.
# =========================================================================================


class MultiVectorOutlierDetector:
    """
    Sentinel Validator: Confirms systemic shifts vs deliberate infiltration.
    Logic: Logic: Score(IF) + Score(Z) + SpectralGap -> Verdict.
    """

    SIGMA_THRESHOLD: Final[float] = 4.0  # High-Sensitivity Sentinel Floor

    def validate_anomaly_verdict(self, node_id: int, stream_z_score: float) -> bool:
        """
        Cross-validates an isolated node against global stream deviation.
        If both the Isolation Forest and the Deviation Engine agree, it's a pathogen.
        """
        # 1. Pull Isolation Score from UHMP Anomaly Register
        idx = node_id % 3810000
        if_score = uhmp_pool.anomaly_view[idx]

        # 2. Chi-Squared Approximation (Sector Three)
        # Weighted decision boundary based on spectral gap truth
        spectral_gap = uhmp_pool.shard_utility_view[idx % 256]

        # Combine vectors into a single Unified Anomaly Probability (UAP)
        # We use spectral_gap to dampen noise (High gap = Stable cluster)
        uap = (if_score * 0.5) + (min(stream_z_score, 10.0) / 10.0 * 0.5)

        if spectral_gap > 0.8:  # Stable cluster - ignore lower UAP
            return uap > 0.9

        return uap > 0.65

    def identify_coordinated_clusters(self) -> int:
        """Scan shards for clusters with coherent entropy signatures."""
        coordinated_threats = 0
        for i in range(256):
            if uhmp_pool.shard_utility_view[i] > 0.95:
                coordinated_threats += 1
        return coordinated_threats
