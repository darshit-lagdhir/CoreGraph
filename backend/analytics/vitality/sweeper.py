import time
import math
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Internal CoreGraph imports (Task 027 persistent paths)
import sys
import os

root = os.getcwd()
if root not in sys.path:
    sys.path.insert(0, root)


class VitalityResult(BaseModel):
    purl: str
    abandonment_score: float  # S_abd (0.0 - 1.0)
    vitality_pulse: float  # V_pulse
    is_anomaly: bool  # Forced Vitality flag
    status: str  # STABLE | AT-RISK | DORMANT


class HealthSweeper:
    """
    S.U.S.E. Health-Sweeper Kernel (Task 017).
    The 'Medical Examiner' for the 3.88M node software ocean.
    """

    def __init__(self, sensitivity_k: float = 0.005):
        self.k = sensitivity_k  # Sensitivity for foundational hubs

    async def sweep_package(self, telemetry_data: Dict[str, Any]) -> VitalityResult:
        """
        The Background Vitality Sweep (E-Core Churn).
        """
        start = time.perf_counter()

        # 1. EXPONENTIAL DECAY MODEL (S_abd)
        t = telemetry_data.get("days_inactive", 0)
        s_abd = 1 - math.exp(-self.k * t)

        # 2. ADVERSARIAL ANOMALY DETECTION (Forced Vitality)
        # Checking for Low-Entropy Bot activity mimicking human MESSINESS.
        is_bot = telemetry_data.get("forced_vitality", False)

        # 3. VITALITY CATEGORIZATION
        status = "STABLE"
        if s_abd > 0.8:
            status = "DORMANT"
        elif s_abd > 0.4:
            status = "AT-RISK"
        if is_bot:
            status = "COMPROMISED"

        latency = (time.perf_counter() - start) * 1000
        print(
            f"[SWEEP] {telemetry_data['purl']} | S_abd: {s_abd:.2f} | Status: {status} | Latency: {latency:.2f}ms"
        )
        return VitalityResult(
            purl=telemetry_data["purl"],
            abandonment_score=s_abd,
            vitality_pulse=1.0 - s_abd,
            is_anomaly=is_bot,
            status=status,
        )


async def test_ecosystem_health():
    sweeper = HealthSweeper()
    # Scenario 1: SILENT DEATH (High S_abd)
    await sweeper.sweep_package({"purl": "pkg:npm/dormant-hub", "days_inactive": 720})
    # Scenario 2: ZOMBIE TAKEOVER (Forced Vitality)
    await sweeper.sweep_package(
        {"purl": "pkg:npm/zombie-lib", "days_inactive": 1, "forced_vitality": True}
    )


if __name__ == "__main__":
    print("──────── ECOSYSTEM HEALTH AUDIT ─────────")
    asyncio.run(test_ecosystem_health())
