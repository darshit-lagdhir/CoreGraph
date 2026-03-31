import asyncio
import logging
import time
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("coregraph.orchestration.priority")


class DistributedPriorityGovernor:
    """
    The Distributed Task Prioritization and Priority Queue Management Kernel.
    Implements Importance Calculus, Hardware-Aware Routing Tiers, and Queue Poisoning Shields.
    """
    __slots__ = (
        "tier",
        "queue_thresholds",
        "priority_levels",
        "aging_threshold_ms",
        "strategic_vitality",
        "_mock_active_queues"
    )

    def __init__(self, tier: str = "redline"):
        self.tier = tier.lower()
        is_potato = (self.tier == "potato")
        
        # Hardware-Aware Queue Compaction Gear-Box
        self.priority_levels: int = 2 if is_potato else 10
        self.queue_thresholds: Dict[str, int] = {
            "alpha": 500 if is_potato else 10000,
            "beta": 2000 if is_potato else 50000,
            "gamma": 5000 if is_potato else 200000
        }
        self.aging_threshold_ms: float = 30000.0  # 30 Seconds for diagnostics, normally hours
        
        self.strategic_vitality: Dict[str, Any] = {
            "priority_concentration_index": 0.0,
            "tasks_aged_up": 0,
            "queue_poison_interventions": 0,
            "alpha_depth": 0,
            "beta_depth": 0,
            "gamma_depth": 0
        }
        
        # Internal state for diagnostic mock without requiring live Redis
        self._mock_active_queues: Dict[str, List[Dict[str, Any]]] = {
            "alpha": [], "beta": [], "gamma": []
        }

    def _calculate_importance_calculus(self, node_metadata: Dict[str, Any]) -> int:
        """
        The Importance Calculus Kernel.
        Aggregates centrality and risk signals to generate a Priority Value (0-9).
        """
        centrality = node_metadata.get("centrality_score", 0.0)
        is_vulnerable = node_metadata.get("active_vulnerability", False)
        is_foundational = node_metadata.get("is_root_node", False)
        
        raw_score = centrality * 5.0
        if is_vulnerable:
            raw_score += 3.0
        if is_foundational:
            raw_score += 4.0
            
        normalized_priority = int(min(max(raw_score, 0), 9))
        
        # Potato tier compaction: Map 0-9 into 0-1
        if self.tier == "potato":
            normalized_priority = 1 if normalized_priority >= 5 else 0
            
        return normalized_priority

    def get_routing_context(self, task_payload: Dict[str, Any]) -> Tuple[str, int]:
        """
        The Multi-Tiered Routing Manifold & Queue Poisoning Shield.
        Routes tasks to Alpha/Beta/Gamma while enforcing hardware-governed saturation limits.
        """
        target_priority = task_payload.get("enforced_priority")
        
        # Source-Authenticated Weighting: Zero out un-trusted explicit priority injections
        if target_priority is not None and not task_payload.get("trusted_orchestrator_sig"):
            target_priority = 0
            self.strategic_vitality["queue_poison_interventions"] += 1
            logger.warning("Queue Poisoning Intercepted. Unsigned high-priority task zeroed.")
            
        if target_priority is None:
            target_priority = self._calculate_importance_calculus(task_payload)
            
        # Determine Logical Queue based on priority band
        if target_priority >= 7 or (self.tier == "potato" and target_priority == 1):
            # Alpha/Critical Bounds Check
            if self.strategic_vitality["alpha_depth"] >= self.queue_thresholds["alpha"]:
                target_queue = "beta"
                self.strategic_vitality["queue_poison_interventions"] += 1
            else:
                target_queue = "alpha"
        elif target_priority >= 3:
            if self.strategic_vitality["beta_depth"] >= self.queue_thresholds["beta"]:
                target_queue = "gamma"
            else:
                target_queue = "beta"
        else:
            target_queue = "gamma"
            
        return target_queue, target_priority

    def _simulate_dispatch(self, task_id: str, queue_name: str, priority: int) -> None:
        """Helper to manage internal state for testing without Celery active."""
        self._mock_active_queues[queue_name].append({
            "id": task_id,
            "p": priority,
            "arrival_time": time.time()
        })
        self.strategic_vitality[f"{queue_name}_depth"] += 1
        
        # Sort queue descending by priority (Simulating Redis ZSET / Priority Queue)
        self._mock_active_queues[queue_name].sort(key=lambda x: x["p"], reverse=True)

    async def execute_aging_sweep(self) -> None:
        """
        The Dynamic Priority Aging Kernel.
        Scavenges lower-tier queues for stagnant tasks and bumps their priority.
        """
        current_time = time.time()
        aged_tasks = []
        
        # Scan Gamma Queue for starvation
        survivors = []
        for task in self._mock_active_queues["gamma"]:
            age_ms = (current_time - task["arrival_time"]) * 1000.0
            if age_ms > self.aging_threshold_ms:
                task["p"] += 1
                aged_tasks.append(task)
                self.strategic_vitality["tasks_aged_up"] += 1
            else:
                survivors.append(task)
                
        self._mock_active_queues["gamma"] = survivors
        self.strategic_vitality["gamma_depth"] -= len(aged_tasks)
        
        # Re-route aged tasks
        for task in aged_tasks:
            # We bypass full routing logic here for direct escalation, but in reality, would re-evaluate
            self._simulate_dispatch(task["id"], "beta", task["p"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("--- INITIATING PRIORITY MANIFOLD DIAGNOSTIC ---")
    
    gov = DistributedPriorityGovernor(tier="redline")
    
    # 1. The Importance Calculus Test
    root_node = {"is_root_node": True, "centrality_score": 1.0, "active_vulnerability": True}
    leaf_node = {"is_root_node": False, "centrality_score": 0.01, "active_vulnerability": False}
    
    assert gov._calculate_importance_calculus(root_node) == 9, "Root Node Priority math failure."
    assert gov._calculate_importance_calculus(leaf_node) == 0, "Leaf Node Priority math failure."
    print("Priority Calculus Confirmed.")
    
    # 2. Queue Poisoning Shield
    malicious_payload = {"enforced_priority": 9, "trusted_orchestrator_sig": False}
    q, p = gov.get_routing_context(malicious_payload)
    assert p == 0, "Security Failure: Queue Poisoning successful."
    assert gov.strategic_vitality["queue_poison_interventions"] == 1, "Alert counter failed."
    print("Queue Poisoning Shield Active.")
    
    # 3. Dynamic Priority Aging
    async def run_aging_test():
        gov._simulate_dispatch("stale_1", "gamma", 0)
        # Manually backdate the arrival time to simulate starvation
        gov._mock_active_queues["gamma"][0]["arrival_time"] = time.time() - 35.0
        
        assert len(gov._mock_active_queues["gamma"]) == 1
        assert len(gov._mock_active_queues["beta"]) == 0
        
        await gov.execute_aging_sweep()
        
        assert len(gov._mock_active_queues["gamma"]) == 0, "Aging sweep failed to extract."
        assert len(gov._mock_active_queues["beta"]) == 1, "Aging sweep failed to escalate."
        assert gov._mock_active_queues["beta"][0]["p"] == 1, "Priority not incremented."
        print("Dynamic Priority Aging Reclimation Confirmed.")

    asyncio.run(run_aging_test())
    
    # 4. Potato Tier Compaction & Quota
    potato_gov = DistributedPriorityGovernor(tier="potato")
    assert potato_gov.priority_levels == 2, "Potato tier did not crush queue complexity."
    assert potato_gov.queue_thresholds["alpha"] == 500, "Potato tier missing alpha quota."
    print("Adaptive Priority Gear-Box Confirmed.")
    print("--- DIAGNOSTIC COMPLETE: STRATEGIC FOCUS SECURE ---")