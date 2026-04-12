import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional


class DistributedRegistryHealthKernel:
    """
    Module 7: Task 026 - Distributed Registry Health Synchronization and Global Connectivity Audit
    External Senses of the Titan, implementing the Circuit-Breaker Doctrine and Multipoint Consensus.
    """

    __slots__ = (
        "_redis_bus",
        "_tier",
        "_health_map",
        "_probe_interval_ms",
        "_sampling_depth",
        "_worker_reports",
        "_circuit_states",
        "_last_probe_time",
    )

    def __init__(self, redis_bus_mock: Dict[str, Any], tier: str = "redline"):
        self._redis_bus = redis_bus_mock
        self._tier = tier.lower()
        self._health_map: Dict[str, float] = {}
        self._worker_reports: Dict[str, Dict[str, List[float]]] = {}
        self._circuit_states: Dict[str, str] = {}
        self._last_probe_time = time.monotonic()
        self._calibrate_probing_frequency()

    def _calibrate_probing_frequency(self) -> None:
        """Hardware-Aware Diagnostic Gear-Box: Preserves HUD by adjusting probe frequency."""
        if self._tier == "redline":
            self._probe_interval_ms = 2000.0
            self._sampling_depth = 50
        else:
            self._probe_interval_ms = 60000.0
            self._sampling_depth = 5

    async def execute_registry_heartbeat(self, registry_id: str) -> Dict[str, Any]:
        """
        Asynchronous Application-Level Probe Manifold: Verifies analytical engine functionality.
        """
        await asyncio.sleep(0)  # 144Hz HUD Yield Handshake

        # Simulated application-level probe metrics
        status_code = 200.0
        latency_ms = 15.0 if self._tier == "redline" else 85.0
        jitter_std_dev = 1.2

        # S_sync = Status / (Latency * Jitter)
        s_sync = status_code / (latency_ms * jitter_std_dev)

        payload = {"registry_id": registry_id, "s_sync": s_sync, "timestamp": time.monotonic()}

        return payload

    async def register_health_signal(
        self, worker_id: str, registry_id: str, status_metrics: Dict[str, float]
    ) -> str:
        """
        Multipoint Quorum Consensus Logic: Aggregates health signals to verify global truth.
        """
        await asyncio.sleep(0)

        if registry_id not in self._worker_reports:
            self._worker_reports[registry_id] = {}

        if worker_id not in self._worker_reports[registry_id]:
            self._worker_reports[registry_id][worker_id] = []

        self._worker_reports[registry_id][worker_id].append(status_metrics.get("s_sync", 1.0))

        # Check for Quorum (Minimum 3 independent workers for global consensus)
        active_reporters = list(self._worker_reports[registry_id].keys())
        if len(active_reporters) < 3:
            return "AWAITING_QUORUM"

        # Calculate Consensus
        all_s_syncs = []
        for reports in self._worker_reports[registry_id].values():
            all_s_syncs.extend(reports[-5:])  # Look at last 5 reports per worker

        if not all_s_syncs:
            return "UNKNOWN"

        mean_s_sync = statistics.mean(all_s_syncs)
        self._health_map[registry_id] = mean_s_sync

        # Circuit-Breaker State Machine
        previous_state = self._circuit_states.get(registry_id, "GREEN")
        new_state = "GREEN"

        if mean_s_sync < 1.0:
            new_state = "RED"
        elif mean_s_sync < 5.0:
            new_state = "AMBER"

        self._circuit_states[registry_id] = new_state
        self._redis_bus[f"health:{registry_id}"] = new_state

        if previous_state == "RED" and new_state == "GREEN":
            return "STAGGERED_RE_ENTRY_TRIGGERED"

        if new_state == "RED" and previous_state != "RED":
            return "METABOLIC_BACKPRESSURE_TRIGGERED"

        return new_state

    def get_global_availability_coefficient(self) -> float:
        """
        Mathematical validation of Global Availability (Lambda_global).
        """
        if not self._circuit_states:
            return 1.0

        state_weights = {"GREEN": 1.0, "AMBER": 0.5, "RED": 0.0}
        total_weight = sum(state_weights.get(state, 0.0) for state in self._circuit_states.values())

        lambda_global = total_weight / len(self._circuit_states)
        return max(0.0, min(1.0, lambda_global))

    def get_connectivity_entropy(self, registry_id: str) -> float:
        """
        Connectivity Entropy Score (E_conn) reflecting alignment of the cluster reality.
        """
        if registry_id not in self._worker_reports or not self._worker_reports[registry_id]:
            return 1.0

        # Simulating consensus matching for entropy calculation
        total_reports = sum(len(reports) for reports in self._worker_reports[registry_id].values())
        if total_reports == 0:
            return 1.0

        pseudo_consensus_matches = total_reports - len(
            self._worker_reports[registry_id]
        )  # Idealized cluster agreement minus distinct sources

        e_conn = 1.0 - (max(0, pseudo_consensus_matches) / total_reports)
        return max(0.0, min(1.0, e_conn))
