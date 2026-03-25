import time
import random
import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ChaosRule(BaseModel):
    latency_ms: int = 0
    drop_rate: float = 0.0 # 0.0 to 1.0
    status_code: int = 200
    retry_after: int = 0
    burst_count: int = 0 # If set, apply for exactly N requests
    
class ChaosStateManager:
    """
    S.U.S.E. Network Chaos Logic (Task 006).
    In-memory singleton for weaponized network state.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChaosStateManager, cls).__new__(cls)
            cls._instance.rules: Dict[str, ChaosRule] = {}
        return cls._instance

    def set_rule(self, target: str, rule: ChaosRule):
        self.rules[target] = rule

    def clear_rules(self):
        self.rules = {}

    async def apply_chaos(self, target: str, response_data: Any) -> tuple[int, Any, Dict[str, str]]:
        """
        Applies active degradation rules to the response.
        Returns (status_code, body, headers)
        """
        rule = self.rules.get(target) or self.rules.get("global")
        headers = {}

        if not rule:
            return 200, response_data, headers

        # 1. LATENCY SPIKE (Asynchronous Non-Blocking)
        if rule.latency_ms > 0:
            await asyncio.sleep(rule.latency_ms / 1000.0)

        # 2. STOCHASTIC PACKET DROP (Forceful Termination)
        if rule.drop_rate > 0 and random.random() < rule.drop_rate:
            # We simulate a "Truncated Payload" by slicing the JSON string
            if isinstance(response_data, str):
                response_data = response_data[:len(response_data) // 2]
            elif isinstance(response_data, (dict, list)):
                raw = str(response_data)
                response_data = raw[:len(raw) // 2]
            return 200, response_data, {"X-Chaos-Dropped": "true"}

        # 3. HTTP STATUS CODE DEGRADATION
        status_code = rule.status_code
        if status_code == 429 and rule.retry_after > 0:
            headers["Retry-After"] = str(rule.retry_after)

        # 4. BURST DECREMENT
        if rule.burst_count > 0:
            rule.burst_count -= 1
            if rule.burst_count <= 0:
                del self.rules[target]

        return status_code, response_data, headers

chaos_manager = ChaosStateManager()
