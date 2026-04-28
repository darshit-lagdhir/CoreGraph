import os
import psutil
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class MetabolicMode(Enum):
    BEAST = "SOVEREIGN_LOCAL"
    LEAN = "CONSTRAINED_CLOUD"


class EnvironmentSentryKernel:
    """
    SECTOR BETA: Environment Sentry Kernel.
    Performs heuristic system probes to bifurcate the Titan's metabolism.
    """

    def __init__(self):
        self.mode = MetabolicMode.LEAN  # Default to safest state (Sector Eta)
        self.is_render = False

    def probe_substrate(self) -> MetabolicMode:
        """
        Sector Alpha: Systemic Detection Heuristics.
        Probes RAM, CPU, and Env Manifests to model the physical reality.
        """
        total_ram = psutil.virtual_memory().total
        cpu_count = os.cpu_count() or 1

        # Sector Beta: Multi-Layered Verification
        is_render_env = os.getenv("RENDER") == "true" or os.getenv("RENDER_SERVICE_ID") is not None

        # Rule: 1GB RAM threshold for Beast-Mode certification
        if total_ram > 1024 * 1024 * 1024 and not is_render_env:
            self.mode = MetabolicMode.BEAST
            logger.info(
                f"[Beta] ENVIRONMENT_CERTIFIED: {self.mode.value} (RAM: {total_ram//(1024**2)}MB, CPU: {cpu_count})"
            )
        else:
            self.mode = MetabolicMode.LEAN
            self.is_render = True
            logger.info(
                f"[Beta] ENVIRONMENT_CERTIFIED: {self.mode.value} (RAM: {total_ram//(1024**2)}MB, CPU: {cpu_count})"
            )

        return self.mode

    def get_context_stats(self) -> dict:
        return {
            "host": os.getenv("HOSTNAME", "SOVEREIGN_WORKSTATION"),
            "arch": os.uname().machine if hasattr(os, "uname") else "x86_64",
            "mode": self.mode.value,
        }
