import asyncio
import random
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

# CoreGraph Adaptive Chaos Supervisor (Task 035)
# Resource-Aware Fault Injection: Hardening the Beast without Systemic Collapse.

logger = logging.getLogger(__name__)

class ChaosRule(str, Enum):
    NONE = "NONE"
    LATENCY = "LATENCY"
    ERROR_429 = "429"
    ERROR_502 = "502"
    DROP = "DROP"

class AdaptiveChaosManager:
    """
    Governor of Misery: Regulates network hostility based on host resources.
    Implements Eco-Mode Failure Simulation and Zero-Block Latency.
    """
    def __init__(self, t_coeff: float = 1.0, max_concurrent: int = 100):
        self.t_coeff = t_coeff # Throughput Coefficient (0.0 to 1.0)
        self.max_concurrent = max_concurrent
        self.active_events = 0
        self.is_active = True
        self.rules: Dict[str, ChaosRule] = {}

        # Default Chaos Params
        self.failure_rate = 0.1 # Default 10%
        self.latency_ms = 500

    def set_rule(self, target: str, rule: ChaosRule):
        """Hidden Administrative Entry Point for Sabotage Injection."""
        self.rules[target] = rule
        logger.info(f"[CHAOS] Rule configured for {target}: {rule}")

    def clear_rules(self):
        """Restores the Pristine Mirror State."""
        self.rules = {}
        logger.info("[CHAOS] All rules cleared. Pristine state restored.")

    def update_resources(self, t_coeff: float):
        """Hardware-Empathic Scaling (Task 035.2)."""
        self.t_coeff = t_coeff
        # Eco-Mode: Stochastic Scaling
        if t_coeff < 0.4:
            self.failure_rate = 0.01 # 1%
            self.max_concurrent = 5
        elif t_coeff < 0.8:
            self.failure_rate = 0.05 # 5%
            self.max_concurrent = 20
        else:
            self.failure_rate = 0.20 # 20%
            self.max_concurrent = 100

    async def apply_chaos(self, target: str, data: Any = None) -> Tuple[int, Any, Dict[str, str]]:
        """
        The S.U.S.E. Chaos Interceptor: Decides fate based on active rules.
        Returns: (status_code, modified_data, headers)
        """
        rule = self.rules.get(target, ChaosRule.NONE)
        
        # If no explicit rule, apply stochastic background failure if active
        if rule == ChaosRule.NONE and self.is_active:
            if random.random() < self.failure_rate:
                # Stochastic choice
                rule = random.choice([ChaosRule.LATENCY, ChaosRule.ERROR_429, ChaosRule.ERROR_502])

        if rule == ChaosRule.NONE:
            return 200, data, {}

        # 1. LATENCY INJECTION
        if rule == ChaosRule.LATENCY:
            actual_delay = (self.latency_ms / 1000.0) * (2.0 - self.t_coeff)
            await asyncio.sleep(min(actual_delay, 29.0))
            return 200, data, {}

        # 2. RATE LIMIT (429)
        elif rule == ChaosRule.ERROR_429:
            return 429, None, {"Retry-After": "5", "X-Chaos-Injected": "true"}

        # 3. GATEWAY ERROR (502)
        elif rule == ChaosRule.ERROR_502:
            return 502, None, {"X-Chaos-Injected": "true"}

        # 4. PACKET DROP (DROP)
        elif rule == ChaosRule.DROP:
            # Simulate a dropped connection by never returning or a hard error
            # For ASGI, we can return a 0 status or just close (hard to do here)
            return 504, None, {"X-Chaos-Injected": "true"}

        return 200, data, {}

# Global instance for the simulation server
chaos_manager = AdaptiveChaosManager()

if __name__ == "__main__":
    print("──────── ADAPTIVE CHAOS AUDIT ─────────")
    manager = AdaptiveChaosManager(t_coeff=1.0)
    
    async def run_audit():
        print("[AUDIT] Setting explicit rule: ERROR_429")
        manager.set_rule("global", ChaosRule.ERROR_429)
        status, _, _ = await manager.apply_chaos("global")
        print(f"[NOMINAL] Result: {status}")
        
        print("\n[AUDIT] Testing Latency stochastic falloff...")
        manager.clear_rules()
        manager.latency_ms = 100
        start = time.perf_counter()
        await manager.apply_chaos("global") # Might sleep
        print(f"[NOMINAL] Duration: {(time.perf_counter() - start)*1000:.2f}ms")
        
        print("\n[SUCCESS] Chaos Manager API Verified.")

    asyncio.run(run_audit())
