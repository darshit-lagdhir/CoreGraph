import asyncio
import heapq
import time
import random
from typing import Dict, List, Set, Tuple, Any, Optional


class GlobalIngestionScheduler:
    """
    Module 4 - Task 019: Global Intake Scheduler.
    Strategic Multi-Registry Crawler Governor utilizing temporal jitter,
    O(log N) prioritized heap dispatching, and distributed lease reclamation.
    """

    __slots__ = (
        "_governor",
        "_active_leases",
        "_registry_health",
        "_hardware_tier",
        "_frontier_limit",
        "_priority_heap",
        "_base_ttl",
        "_hibernated_ecosystems",
    )

    def __init__(self, governor: Any = None, hardware_tier: str = "redline"):
        self._governor = governor
        self._hardware_tier = hardware_tier
        self._base_ttl = 86400.0  # 24 hours Standard Decay

        self._active_leases: Dict[str, float] = {}
        self._priority_heap: List[Tuple[float, float, str, Dict[str, Any]]] = []
        self._hibernated_ecosystems: Set[str] = set()

        self._registry_health: Dict[str, Dict[str, float]] = {
            "npm": {"latency": 0.0, "success": 1.0},
            "pypi": {"latency": 0.0, "success": 1.0},
            "cargo": {"latency": 0.0, "success": 1.0},
            "github": {"latency": 0.0, "success": 1.0},
        }

        if self._hardware_tier == "redline":
            self._frontier_limit = 10000
        else:
            self._frontier_limit = 200

    def calculate_priority_weight(self, c_topo: float, r_pathogen: float, a_churn: float) -> float:
        """Calculates the Forensic Priority Weight (W)."""
        return (c_topo * 0.5) + (r_pathogen * 0.3) + (a_churn * 0.2)

    def calculate_next_ttl(self, weight: float) -> float:
        """Applies Monotonic TTL decay logic with Temporal Jitter."""
        ttl_next = self._base_ttl * (1.0 / (1.0 + weight))
        jitter = random.uniform(-0.1 * ttl_next, 0.1 * ttl_next)
        return ttl_next + jitter

    async def monitor_registry_availability(
        self, ecosystem: str, latency_ms: float, success_ratio: float
    ) -> None:
        """
        Updates ecosystem health matrices and triggers Phalanx Hibernation
        if Latency > 2000ms or Success < 90%.
        """
        if ecosystem not in self._registry_health:
            return

        self._registry_health[ecosystem]["latency"] = latency_ms
        self._registry_health[ecosystem]["success"] = success_ratio

        if latency_ms > 2000.0 or success_ratio < 0.90:
            self._hibernated_ecosystems.add(ecosystem)
        else:
            self._hibernated_ecosystems.discard(ecosystem)

    def stage_nodes_for_ingestion(self, raw_nodes: List[Dict[str, Any]]) -> None:
        """
        Injects cold nodes or expired state entries into the priority multiplexer.
        Nodes must contain: id, ecosystem, c_topo, r_pathogen, a_churn.
        """
        current_time = time.time()
        for node in raw_nodes:
            node_id = node.get("id", "")
            if not node_id or node_id in self._active_leases:
                continue

            ecosystem = node.get("ecosystem", "npm")
            if ecosystem in self._hibernated_ecosystems:
                continue

            if self._hardware_tier == "redline":
                weight = self.calculate_priority_weight(
                    node.get("c_topo", 0.0), node.get("r_pathogen", 0.0), node.get("a_churn", 0.0)
                )
            else:
                # Lazy Priority for Potato Hardware Tier
                weight = node.get("c_topo", 0.0) * 0.5

            # Invert weight for min-heap to simulate max-heap extraction
            heapq.heappush(self._priority_heap, (-weight, current_time, node_id, node))

    async def dispatch_next_wave(self) -> List[Dict[str, Any]]:
        """
        Populates the Active Frontier and acquires distributed leases.
        Returns nodes to be routed to the governor's ingestion phalanx.
        """
        dispatched_wave = []
        current_time = time.time()

        while self._priority_heap and len(self._active_leases) < self._frontier_limit:
            weight_inv, _, node_id, node = heapq.heappop(self._priority_heap)

            ecosystem = node.get("ecosystem", "npm")
            if ecosystem in self._hibernated_ecosystems:
                continue

            self._active_leases[node_id] = current_time
            dispatched_wave.append(node)

        # External dispatch integration signal
        if self._governor and hasattr(self._governor, "enqueue_batch"):
            if asyncio.iscoroutinefunction(self._governor.enqueue_batch):
                await self._governor.enqueue_batch(dispatched_wave)
            else:
                self._governor.enqueue_batch(dispatched_wave)

        return dispatched_wave

    async def manage_task_leases(self, timeout_sec: float = 300.0) -> int:
        """
        Scans the Active Frontier for stale task leases and forcefully reclaims
        them to prevent structural topological deadlocks.
        """
        current_time = time.time()
        reclaimed_count = 0
        stale_keys = []

        for node_id, lease_timestamp in self._active_leases.items():
            if (current_time - lease_timestamp) > timeout_sec:
                stale_keys.append(node_id)

        for key in stale_keys:
            del self._active_leases[key]
            reclaimed_count += 1

        return reclaimed_count

    def release_lease(self, node_id: str) -> None:
        """Called by downstream persistence workers upon successful materialization."""
        self._active_leases.pop(node_id, None)

    def dump_telemetry(self) -> Dict[str, Any]:
        """Emits zero-copy IPC signals for the Master Control HUD overlay."""
        return {
            "active_leases": len(self._active_leases),
            "heap_depth": len(self._priority_heap),
            "hibernated_ecosystems": list(self._hibernated_ecosystems),
            "frontier_limit": self._frontier_limit,
            "registry_health": self._registry_health,
        }
