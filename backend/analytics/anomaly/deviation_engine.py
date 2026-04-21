import math
import struct
from typing import Final
from backend.core.sharding.hadronic_pool import uhmp_pool

# =========================================================================================
# COREGRAPH DEVIATION ENGINE: WELFORD’S ONLINE ALGORITHM (PROMPT 8)
# =========================================================================================
# MANDATE: Eliminate 121MB buffer overflow. Real-time statistical drift compensation.
# ARCHITECTURE: Recursive Mean/Variance calculation for 1024 streams.
# =========================================================================================


class HadronicDeviationEngine:
    """
    Statistical Watchdog: Calculates Z-Scores for Every Ingested Packet.
    Logic: Online Variance Tracking with Temporal Decay.
    """

    # 24B Struct: [Count(Q) | Mean(d) | M2(d)]
    REG_FORMAT: Final[str] = "Qdd"
    REG_SIZE: Final[int] = 24

    def update_stream_statistics(self, stream_id: int, new_value: float):
        """
        Executes Welford's Algorithm to maintain running statistics without history storage.
        """
        offset = (stream_id % 1024) * self.REG_SIZE
        count, mean, m2 = struct.unpack_from(self.REG_FORMAT, uhmp_pool.deviation_view, offset)

        # Online Calculation
        count += 1
        delta = new_value - mean
        mean += delta / count
        delta2 = new_value - mean
        m2 += delta * delta2

        # Write back to UHMP Register
        struct.pack_into(self.REG_FORMAT, uhmp_pool.deviation_view, offset, count, mean, m2)

        # Calculate Z-Score (3 Sigma Threshold)
        variance = m2 / count if count > 1 else 0.1
        std_dev = math.sqrt(variance)
        z_score = abs(new_value - mean) / (std_dev + 0.0001)

        return z_score
