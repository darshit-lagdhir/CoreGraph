import asyncio
import time
import collections
import logging
from enum import Enum, auto
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreakerOpenException(Exception):
    """Fail-Fast exception raised when a registry sector is experiencing systemic outage."""

    def __init__(self, registry_id: str, message: str = "Circuit Breaker OPEN"):
        super().__init__(f"{message} for {registry_id}")
        self.registry_id = registry_id


class DLQForensicPacket:
    """
    Slotted DTO tracking absolute failed request metadata.
    Enforces the 'Unreachable Truth' mandate mapping syntax, network arrays, and registry nodes natively.
    """

    __slots__ = (
        "purl",
        "registry_id",
        "batch_uuid",
        "status_code",
        "stack_trace",
        "query_fragment",
        "timestamp",
    )

    def __init__(
        self,
        purl: str,
        registry_id: str,
        batch_uuid: str,
        status_code: int,
        stack_trace: str,
        query_fragment: str,
    ):
        self.purl = purl
        self.registry_id = registry_id
        self.batch_uuid = batch_uuid
        self.status_code = status_code
        self.stack_trace = stack_trace
        self.query_fragment = query_fragment
        self.timestamp = time.time()


class RegistryStateMap:
    """
    Slotted tracking logic evaluating specific registry Failure Densities vs rolling execution success arrays.
    """

    __slots__ = (
        "state",
        "failure_history",
        "last_state_change",
        "probing_success_count",
        "probing_total_count",
        "window_size",
    )

    def __init__(self, window_size: int = 1000):
        self.state = CircuitState.CLOSED
        # Deque of booleans: True for failure, False for success
        self.failure_history: collections.deque = collections.deque(maxlen=window_size)
        self.last_state_change = time.time()
        self.probing_success_count = 0
        self.probing_total_count = 0
        self.window_size = window_size

    @property
    def failure_density(self) -> float:
        if not self.failure_history:
            return 0.0
        return sum(1 for failure in self.failure_history if failure) / len(self.failure_history)


class TelemetryCircuitBreaker:
    """
    Module 5 - Task 014: Circuit Breaker Kernel and Terminal Failure Circuitry.
    The primary tactical regulator intercepting fail-fast anomalies and orchestrating
    asynchronous Dead Letter Queue (DLQ) persistent flushes.
    """

    __slots__ = (
        "_hardware_tier",
        "_registry_states",
        "_dlq_buffer",
        "_tripping_threshold",
        "_cooldown_duration_sec",
        "_probing_threshold",
        "_is_shutting_down",
        "_flush_daemon_task",
    )

    def __init__(self, hardware_tier: str = "redline"):
        self._hardware_tier = hardware_tier
        self._registry_states: Dict[str, RegistryStateMap] = collections.defaultdict(
            RegistryStateMap
        )
        self._dlq_buffer: List[DLQForensicPacket] = []
        self._is_shutting_down = False

        # Hardware-Aware Resilience Gear-Box
        if self._hardware_tier == "redline":
            self._tripping_threshold = 0.15  # 15% Failure Rate
            self._cooldown_duration_sec = 30.0  # Aggressive Recovery
        else:
            self._tripping_threshold = 0.40  # 40% Failure Rate
            self._cooldown_duration_sec = 300.0  # Conservative Stability

        self._probing_threshold = 0.95  # Require 95% success rate for Half-Open closure
        self._flush_daemon_task = asyncio.create_task(self._dlq_flush_daemon())

    async def intercept_request(self, registry_id: str) -> None:
        """
        'Fail-Fast' Interceptor bridging Telemetry execution calls against Systemic Registry State Maps.
        Rejects immediately avoiding downstream GIL accumulation if limits collapse.
        """
        state_map = self._registry_states[registry_id]

        if state_map.state == CircuitState.OPEN:
            # Check for Cooldown Transistion
            if time.time() - state_map.last_state_change > self._cooldown_duration_sec:
                self._transition_state(registry_id, CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenException(registry_id)

        elif state_map.state == CircuitState.HALF_OPEN:
            # Artificial rate-limiting logic could be mapped securely here allowing solely the 'Probing Phalanx'
            state_map.probing_total_count += 1

    def record_success(self, registry_id: str) -> None:
        """Evaluates operational closure bounds and resets error arrays natively."""
        state_map = self._registry_states[registry_id]

        if state_map.state == CircuitState.CLOSED:
            state_map.failure_history.append(False)

        elif state_map.state == CircuitState.HALF_OPEN:
            state_map.probing_success_count += 1
            recovery_prob = state_map.probing_success_count / max(1, state_map.probing_total_count)

            if state_map.probing_total_count >= 10 and recovery_prob >= self._probing_threshold:
                self._transition_state(registry_id, CircuitState.CLOSED)

    def record_failure(self, registry_id: str) -> None:
        """Logs systemic collisions and initiates fail-fast triggers preventing Event-Loop zombies."""
        state_map = self._registry_states[registry_id]

        if state_map.state == CircuitState.CLOSED:
            state_map.failure_history.append(True)

            # Calculate density against thresholds
            if (
                len(state_map.failure_history) >= 20
                and state_map.failure_density >= self._tripping_threshold
            ):
                logging.critical(
                    f"[CIRCUIT BREAKER] {registry_id} density {state_map.failure_density:.2%} breached. Tripping OPEN."
                )
                self._transition_state(registry_id, CircuitState.OPEN)

        elif state_map.state == CircuitState.HALF_OPEN:
            logging.warning(f"[CIRCUIT BREAKER] {registry_id} probing failed. Reverting to OPEN.")
            self._transition_state(registry_id, CircuitState.OPEN)

    def _transition_state(self, registry_id: str, new_state: CircuitState) -> None:
        """Updates physics variables preserving specific temporal states."""
        state_map = self._registry_states[registry_id]
        state_map.state = new_state
        state_map.last_state_change = time.time()

        if new_state == CircuitState.CLOSED:
            state_map.failure_history.clear()

        elif new_state == CircuitState.HALF_OPEN:
            state_map.probing_success_count = 0
            state_map.probing_total_count = 0

        elif new_state == CircuitState.OPEN:
            pass  # External forced termination triggers hook here in production runtime

    def _handoff_to_dlq(
        self,
        purl: str,
        registry_id: str,
        status_code: int,
        stack_trace: str,
        query_fragment: str,
        batch_uuid: str,
    ) -> None:
        """
        Asynchronous Write Handler pushing to Memory Buffers instead of Relational Arrays
        effectively saving I/O Bandwidth.
        """
        packet = DLQForensicPacket(
            purl, registry_id, batch_uuid, status_code, stack_trace, query_fragment
        )
        self._dlq_buffer.append(packet)

    async def _dlq_flush_daemon(self) -> None:
        """Background coroutine flushing volatile memory failure buffers to Silicon Arrays."""
        while not self._is_shutting_down:
            await asyncio.sleep(5.0)
            if self._dlq_buffer:
                await self._flush_failure_buffer()

    async def _flush_failure_buffer(self) -> None:
        """Simulation logic targeting the CoreGraph Postgres persistence vault via atomic bulk inserts."""
        # packets_flushed = len(self._dlq_buffer)
        self._dlq_buffer.clear()
        # In a real environment, trigger UPSERT operation natively bridging the forensic array mappings.
        pass

    def initiate_shutdown(self) -> None:
        """Safely ends async DAEMON locks to avoid Python interpreter warnings."""
        self._is_shutting_down = True
        if self._flush_daemon_task:
            self._flush_daemon_task.cancel()
