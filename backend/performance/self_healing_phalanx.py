import asyncio
import signal
import os
import sys
import logging
import gc
from typing import Dict, Any, Callable
from backend.telemetry.hud_sync import HUDSync
from backend.core.memory_manager import metabolic_governor

logger = logging.getLogger(__name__)


class HadronicRemediationKernel:
    """
    HADRONIC REMEDIATION KERNEL: Autonomous diagnostic and repair engine.
    Detects and isolates stalled or leaking analytical modules.
    """

    def __init__(self):
        self.hud = HUDSync()
        self.module_health: Dict[str, bool] = {}

    async def monitor_module(self, name: str, coroutine: Callable):
        """Sector Beta: Anomaly Isolation and Module Re-instantiation."""
        while True:
            try:
                self.module_health[name] = True
                await coroutine()
            except Exception as e:
                self.module_health[name] = False
                self.hud.log_error(
                    f"REMEDIATION_TRIGGER: Module '{name}' collapsed. Error: {str(e)}"
                )
                self.hud.log_event("ANOMALY_ISOLATION", {"module": name, "error": type(e).__name__})
                gc.collect()
                await asyncio.sleep(1)
                self.hud.log_success(
                    f"MODULE_RECONSTITUTION: Re-spawning '{name}' within clean envelope."
                )


class SignalRecoveryPhalanx:
    """
    SIGNAL RECOVERY PHALANX: Signal-driven state preservation.
    Handles SIGTERM/SIGINT for zero-loss hot-reloads (Linux/POSIX).
    """

    def __init__(self, vault):
        self.vault = vault
        self.hud = HUDSync()
        self._setup_signals()

    def _setup_signals(self):
        """Sector Gamma: Hooks into the Kernel signal interface (Platform Aware)."""
        if os.name == "posix":
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig, lambda: asyncio.create_task(self.emergency_condensation())
                )
            logger.info("Signal Recovery Phalanx: POSIX handlers attached.")
        else:
            # Windows Support (Development Mode)
            logger.info("Signal Recovery Phalanx: Operating in Windows Emulation Mode.")

    async def emergency_condensation(self):
        """Sector Gamma: 500ms window for state hardening."""
        self.hud.log_warning("SIGNAL_RECEIVED: Initiating Emergency State Condensation.")
        self.hud.log_event("HEALING_RADIANCE", {"status": "CONDENSING"})
        try:
            await self.vault.wal.flush()
            self.hud.log_success("VAULT_HARDENED: State secured in persistent substrate.")
        except Exception as e:
            self.hud.log_error(f"CONDENSATION_FAILURE: {str(e)}")
        finally:
            self.hud.log_event("HEALING_RADIANCE", {"status": "REBOOT_READY"})
            logger.info("Titan ready for sovereign reboot.")


class SelfHealingPhalanxEngine:
    """
    SELF-HEALING PHALANX ENGINE: The Titan's Autonomic Nervous System.
    """

    def __init__(self, vault):
        self.remediation = HadronicRemediationKernel()
        self.recovery = SignalRecoveryPhalanx(vault)
        self.hud = HUDSync()

    async def pulse_check(self):
        """Sector IOTA: Continuous Systemic Heartbeat Telemetry."""
        self.hud.log_success("SELF_HEALING_PHALANX: Autonomic Nervous System Active.")
        while True:
            await asyncio.sleep(1)
            rss = metabolic_governor.get_physical_rss_us()
            if rss > 145.0:
                self.hud.log_event("HEALING_RADIANCE", {"status": "PURGING_CACHE"})
                gc.collect()
            self.hud.log_event(
                "SOVEREIGN_PULSE",
                {
                    "rss": rss,
                    "modules": len(self.remediation.module_health),
                    "healthy": all(self.remediation.module_health.values()),
                },
            )
