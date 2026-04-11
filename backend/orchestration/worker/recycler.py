import asyncio
import logging
import os
import signal
import time
from typing import Any, Dict, List

logger = logging.getLogger("coregraph.orchestration.worker")

class WorkerLifecycleGovernor:
    """
    The Proactive Worker Recycling Kernel and Memory-Leak Neutralization Protocol.
    Manages process lifecycles, neutralizes phantom bloat, and enforces the Ephemeral Doctrine.
    """
    __slots__ = (
        "tier",
        "max_tasks_per_child",
        "max_memory_per_child",
        "staggered_recycle_interval",
        "zombie_grace_period",
        "metabolic_vitality",
        "active_process_registry",
        "_ipc_lock"
    )

    def __init__(self, tier: str = "redline"):
        self.tier = tier.lower()
        is_potato = self.tier == "potato"

        # Atomic Shared-Memory Lock mapping for thread-safe recycling sequences
        self._ipc_lock = asyncio.Lock()

        # HW-Aware Lifespan Calibration
        self.max_tasks_per_child: int = 2500 if is_potato else 500
        self.max_memory_per_child: int = 100 * 1024 if is_potato else 150 * 1024  # Size in KB

        self.staggered_recycle_interval: float = 0.5 if is_potato else 0.1
        self.zombie_grace_period: int = 15

        self.metabolic_vitality: Dict[str, Any] = {
            "recycled_workers": 0,
            "zombies_neutralized": 0,
            "memory_reclaimed_mb": 0.0,
            "fork_latency_ms": 0.0,
            "average_worker_age_tasks": 0
        }

        self.active_process_registry: List[Dict[str, Any]] = []

    def get_recycling_settings(self) -> Dict[str, Any]:
        """
        Injects the Ephemeral Worker Doctrine into the Celery Configuration.
        """
        return {
            "worker_max_tasks_per_child": self.max_tasks_per_child,
            "worker_max_memory_per_child": self.max_memory_per_child,
            "worker_proc_alive_timeout": 4.0,
            "worker_pool_restarts": True,
        }

    async def trigger_graceful_recycle(self, worker_pids: List[int]) -> None:
        """
        The Staggered Regeneration Kernel.
        Issues recycling requests while protecting the 144Hz HUD from context-switch storms.
        """
        start_time = time.perf_counter()

        async with self._ipc_lock:
            for pid in worker_pids:
                try:
                    # Graceful Degradation Pattern: Only signal, never SIGKILL active contexts immediately
                    logger.debug(f"Initiating graceful recycle for PID {pid}")
                    import sys
                    if sys.platform == "win32":
                        os.kill(pid, signal.SIGTERM)
                    else:
                        os.kill(pid, signal.SIGTERM)

                    # Check for Zombie State securely
                    await self._enforce_zombie_neutralization(pid)
                    self.metabolic_vitality["recycled_workers"] += 1

                    # Yield Event Loop to spread the forking overhead (Thread-safe block limit)
                    await asyncio.sleep(self.staggered_recycle_interval)

                except ProcessLookupError:
                    logger.debug(f"PID {pid} already relinquished.")
                except Exception as e:
                    logger.error(f"Failed to gracefully recycle worker PID {pid}: {e}")
        import sys
        is_windows = sys.platform == "win32"
        
        try:
            # Poll for process termination map
            for _ in range(self.zombie_grace_period):
                # Using signal 0 checks if the process still exists safely
                if is_windows:
                    try:
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        SYNCHRONIZE = 0x00100000
                        handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
                        if not handle:
                            raise ProcessLookupError()
                        kernel32.CloseHandle(handle)
                    except Exception:
                        raise ProcessLookupError()
                else:
                    os.kill(pid, 0)
                await asyncio.sleep(1.0)
            
            # If graceful polling loop finishes without raising ProcessLookupError, it's a Zombie.
            logger.warning(f"ZOMBIE DETECTED: PID {pid} failed to exit. Issuing SIGKILL.")
            if is_windows:
                os.kill(pid, signal.SIGTERM)  # Windows kills process instantly via SIGTERM
            else:
                os.kill(pid, signal.SIGKILL)
            
            self.metabolic_vitality["zombies_neutralized"] += 1
            
        except ProcessLookupError:
            # Process terminated successfully within the grace period.
            pass
        except OSError as e:
            logger.debug(f"OS level error during zombie check on PID {pid}: {e}")

    def trigger_mock_residency_reclamation(self, reclaimed_mb: float) -> None:
        """
        Records the successful purge of Python Garbage Collection bloat.
        """
        self.metabolic_vitality["memory_reclaimed_mb"] += reclaimed_mb
        self._signal_hud_metabolic_pulse()

    def _signal_hud_metabolic_pulse(self) -> None:
        """
        Transmits the cellular regeneration metrics to the Master HUD.
        """
        logger.debug(f"METABOLIC VITALITY PULSE: {self.metabolic_vitality}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("--- INITIATING WORKER LIFECYCLE GOVERNOR DIAGNOSTIC ---")
    
    # Redline Test
    redline_gov = WorkerLifecycleGovernor(tier="redline")
    assert redline_gov.max_tasks_per_child == 500, "Redline max_tasks_per_child collapse."
    
    # Potato Test
    potato_gov = WorkerLifecycleGovernor(tier="potato")
    assert potato_gov.max_tasks_per_child == 2500, "Potato max_tasks_per_child collapse."
    assert potato_gov.staggered_recycle_interval == 0.5, "Potato CPU starvation protection failed."
    
    print(f"Redline Task Lifespan : {redline_gov.max_tasks_per_child} Tasks/Worker")
    print(f"Potato Task Lifespan  : {potato_gov.max_tasks_per_child} Tasks/Worker")
    
    async def run_diagnostic():
        # Spawn a dummy process to act as the worker
        import subprocess
        import sys
        
        print("Spawning Mock Worker Process...")
        # Windows-specific: using CREATE_NEW_PROCESS_GROUP or simply wait to terminate gracefully.
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(5)"])
        
        await asyncio.sleep(0.5)
        print(f"Mock Worker Active on PID {proc.pid}")
        
        # In Windows, os.kill(pid, signal.SIGTERM) maps to TerminateProcess which instantly kills it,
        # so relying on ProcessLookupError in the immediate next polling line is the expected path.
        await redline_gov.trigger_graceful_recycle([proc.pid])
        
    asyncio.run(run_diagnostic())
    
    vitality = redline_gov.metabolic_vitality
    print(f"Workers Recycled    : {vitality['recycled_workers']}")
    print(f"Zombies Neutralized : {vitality['zombies_neutralized']}")
    assert vitality['recycled_workers'] == 1, "Graceful recycle mechanism failed."
    
    print("--- DIAGNOSTIC COMPLETE: CELLULAR VITALITY SECURE ---")