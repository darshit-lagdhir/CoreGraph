import json
import math
import os
import random
import time
from typing import Callable, List


class ChaosEngine:
    """Poisson-based failure injection harness for workstation-level stress testing."""

    def __init__(self, lambda_factor: float = 0.5):
        self.lambda_factor = lambda_factor

    def poisson_probability(self, k: int) -> float:
        """Calculate P(k events)."""
        return (math.pow(self.lambda_factor, k) * math.exp(-self.lambda_factor)) / math.factorial(k)

    def trigger_chaos(self):
        """Run a Chaos Sprint injecting scheduled failures."""
        k = random.randint(0, 3)
        prob = self.poisson_probability(k)
        if random.random() < prob:
            print(f"Injecting chaos... (k={k})")
            self._execute_random_corruptor()

    def _execute_random_corruptor(self):
        corruptors = [
            self.corrupt_migration_checksum,
            self.revoke_gpg_entropy,
            self.poison_task_registry,
        ]
        random.choice(corruptors)()

    def corrupt_migration_checksum(self):
        print("Executing: corrupt_migration_checksum - Transactional DDL rollback test")

    def revoke_gpg_entropy(self):
        print("Executing: revoke_gpg_entropy - GPG agent heartbeat service check")

    def poison_task_registry(self):
        print("Executing: poison_task_registry - Registry Validation Scripts check")
        try:
            with open(".workspace/task-matrix.json", "r+") as f:
                data = json.load(f)
                data["current_status"]["poisoned"] = True
                f.seek(0)
                json.dump(data, f)
        except Exception:
            pass


if __name__ == "__main__":
    engine = ChaosEngine(lambda_factor=5.0)
    engine.trigger_chaos()
