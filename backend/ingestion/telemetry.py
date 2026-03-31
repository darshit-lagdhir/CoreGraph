"""
Central Nervous System and Diagnostic Signaling Kernel.
High-Density Asynchronous Telemetry, Zombie Worker Heuristics, and Differential Sampling.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional


class TelemetrySaturationWarning(Exception):
    """Internal signal indicating HUD telemetry bandwidth requires clamping."""

    pass


class IngestionTelemetryKernel:
    __slots__ = (
        "hardware_tier",
        "_worker_vitality",
        "_heartbeat_threshold_ms",
        "_counters",
        "_anomaly_buffer",
        "_hud_signal_queue",
        "_last_vitality_flush",
        "_vitality_interval_ms",
        "_throttling_coefficient",
    )

    def __init__(self, hardware_tier: str):
        self.hardware_tier = hardware_tier
        self._worker_vitality: Dict[int, float] = {}
        self._counters: Dict[str, int] = {
            "nodes_processed": 0,
            "edges_processed": 0,
            "network_timeouts": 0,
            "anomalies_logged": 0,
        }
        self._anomaly_buffer: List[Dict[str, Any]] = []
        self._hud_signal_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._last_vitality_flush = time.perf_counter() * 1000
        self._throttling_coefficient = 1.0

        if self.hardware_tier == "redline":
            self._vitality_interval_ms = 100
            self._heartbeat_threshold_ms = 2000
        elif self.hardware_tier == "potato":
            self._vitality_interval_ms = 500
            self._heartbeat_threshold_ms = 5000
        else:
            self._vitality_interval_ms = 250
            self._heartbeat_threshold_ms = 3000

    def worker_heartbeat(self, worker_id: int) -> None:
        self._worker_vitality[worker_id] = time.perf_counter() * 1000

    def record_throughput(self, nodes: int = 0, edges: int = 0) -> None:
        self._counters["nodes_processed"] += nodes
        self._counters["edges_processed"] += edges
        self._evaluate_vitality_flush()

    def _evaluate_vitality_flush(self) -> None:
        current_time = time.perf_counter() * 1000
        if (current_time - self._last_vitality_flush) >= self._vitality_interval_ms:
            self._last_vitality_flush = current_time

            vitality_packet = {
                "type": "vitality",
                "nodes": self._counters["nodes_processed"],
                "edges": self._counters["edges_processed"],
                "active_workers": len(self._worker_vitality),
            }

            self._push_to_hud(vitality_packet, priority=False)

    def log_anomaly(
        self, anomaly_type: str, forensic_data: Dict[str, Any], priority: bool = False
    ) -> None:
        self._counters["anomalies_logged"] += 1

        packet = {
            "type": "anomaly",
            "anomaly_type": anomaly_type,
            "forensic_data": forensic_data,
            "timestamp": time.perf_counter() * 1000,
        }

        if priority:
            self._push_to_hud(packet, priority=True)
            self._anomaly_buffer.append(packet)
        else:
            # Sampled logging logic: only record 1 in 10 low-level warnings
            if self._counters["anomalies_logged"] % 10 == 0:
                self._anomaly_buffer.append(packet)

    def _push_to_hud(self, packet: Dict[str, Any], priority: bool) -> None:
        try:
            if priority:
                if self._hud_signal_queue.full():
                    self._hud_signal_queue.get_nowait()
                self._hud_signal_queue.put_nowait(packet)
            else:
                if not self._hud_signal_queue.full():
                    self._hud_signal_queue.put_nowait(packet)
        except asyncio.QueueFull:
            pass

    async def extract_hud_signals(self) -> List[Dict[str, Any]]:
        signals = []
        while not self._hud_signal_queue.empty():
            signals.append(self._hud_signal_queue.get_nowait())
            self._hud_signal_queue.task_done()
        return signals

    def monitor_vitality(self) -> List[int]:
        """Returns a list of zombie worker IDs for the governor to recycle."""
        current_time = time.perf_counter() * 1000
        zombies = []
        for worker_id, last_beat in list(self._worker_vitality.items()):
            if (current_time - last_beat) > self._heartbeat_threshold_ms:
                zombies.append(worker_id)
                del self._worker_vitality[worker_id]

        if zombies:
            self._calculate_backpressure(len(zombies))

        return zombies

    def _calculate_backpressure(self, failure_count: int) -> None:
        if failure_count > 0:
            self._throttling_coefficient = max(0.1, self._throttling_coefficient - 0.2)
        else:
            self._throttling_coefficient = min(1.0, self._throttling_coefficient + 0.05)

    def get_backpressure_signal(self) -> float:
        return self._throttling_coefficient

    def fetch_persistent_anomalies(self) -> List[Dict[str, Any]]:
        """Used by the Batch Reconciler to persist the sampled warnings."""
        logs = self._anomaly_buffer.copy()
        self._anomaly_buffer.clear()
        return logs
