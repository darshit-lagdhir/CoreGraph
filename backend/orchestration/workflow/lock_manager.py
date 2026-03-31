import asyncio
import logging
import random
import time
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("coregraph.orchestration.mutex")


class DistributedLockManager:
    """
    The Distributed Mutual Exclusion (Mutex) and Global Task Locking Kernel.
    Implements Atomic Acquisition, Wait-Free Yielding, and LUA-Based Sovereignty Guards.
    """
    __slots__ = (
        "tier",
        "lock_ttl_ms",
        "base_jitter_ms",
        "active_sovereignty_registry",
        "sovereignty_vitality",
        "_lua_release_script",
        "_redis_mock_state"
    )

    def __init__(self, tier: str = "redline"):
        self.tier = tier.lower()
        is_potato = (self.tier == "potato")
        
        # Hardware-Aware TTL & Jitter Gear-Box
        self.lock_ttl_ms: int = 30000 if is_potato else 5000
        self.base_jitter_ms: int = 500 if is_potato else 50
        
        self.active_sovereignty_registry: Dict[str, str] = {}
        
        # LUA script for ID-validated atomic release to prevent Lock Theft
        self._lua_release_script = """
        if redis.call("get",KEYS[1]) == ARGV[1] then
            return redis.call("del",KEYS[1])
        else
            return 0
        end
        """
        
        self.sovereignty_vitality: Dict[str, Any] = {
            "successful_acquisitions": 0,
            "total_attempts": 0,
            "lock_collisions": 0,
            "watchdog_renewals": 0
        }
        
        # Internal state for diagnostic mock without requiring live Redis
        self._redis_mock_state: Dict[str, Tuple[str, float]] = {}

    def _calculate_backoff_jitter(self, attempt_count: int) -> float:
        """
        The Hardware-Aware Contention Attenuation Manifold.
        Calculates Exponential Backoff with randomized jitter to break Thundering Herds.
        """
        base = self.base_jitter_ms * (2 ** attempt_count)
        jitter = random.uniform(0, base * 0.2)
        return (base + jitter) / 1000.0  # Returns seconds

    async def acquire_node_lock(self, package_id: str, worker_id: str) -> Optional[str]:
        """
        The Atomic Acquisition Kernel.
        Simulates SET key val NX PX to guarantee mutual exclusion. Returns Token or None (Yield).
        """
        self.sovereignty_vitality["total_attempts"] += 1
        lock_key = f"cg:lock:{package_id}"
        current_time = time.time()
        
        # ATOMIC ACQUISITION MOCK
        existing = self._redis_mock_state.get(lock_key)
        if existing:
            held_worker, expiry = existing
            if current_time < expiry:
                self.sovereignty_vitality["lock_collisions"] += 1
                return None  # Contention Signal -> Yield and ReQueue
                
        # Lock Secured
        expiry_time = current_time + (self.lock_ttl_ms / 1000.0)
        self._redis_mock_state[lock_key] = (worker_id, expiry_time)
        
        self.active_sovereignty_registry[lock_key] = worker_id
        self.sovereignty_vitality["successful_acquisitions"] += 1
        
        return worker_id  # Emulating the SovereigntyToken

    async def release_node_lock(self, package_id: str, worker_id: str) -> bool:
        """
        The LUA-Based Sovereignty Release Logic.
        Guarantees that a worker only deletes a lock if its UUID still matches the key.
        """
        lock_key = f"cg:lock:{package_id}"
        
        # MOCK LUA SCRIPT EVALUATION
        existing = self._redis_mock_state.get(lock_key)
        if existing and existing[0] == worker_id:
            del self._redis_mock_state[lock_key]
            self.active_sovereignty_registry.pop(lock_key, None)
            return True
            
        logger.warning(f"LOCK THEFT PREVENTED: Worker {worker_id} attempted to release expired lock.")
        return False

    async def spawn_lock_watchdog(self, package_id: str, worker_id: str) -> None:
        """
        The Asynchronous Watchdog Heartbeat.
        Periodically renews the TTL of long-running tasks to prevent Zombie Worker misclassification.
        """
        lock_key = f"cg:lock:{package_id}"
        renewal_interval = (self.lock_ttl_ms / 1000.0) * 0.6  # Renew at 60% of TTL
        
        # Simulate a single renewal tick
        await asyncio.sleep(0.001)
        
        existing = self._redis_mock_state.get(lock_key)
        if existing and existing[0] == worker_id:
            new_expiry = time.time() + (self.lock_ttl_ms / 1000.0)
            self._redis_mock_state[lock_key] = (worker_id, new_expiry)
            self.sovereignty_vitality["watchdog_renewals"] += 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("--- INITIATING LOCK MANAGER KERNEL DIAGNOSTIC ---")
    
    mutex = DistributedLockManager(tier="redline")
    
    async def run_contention_gauntlet():
        target_node = "pkg:npm/lodash"
        
        # 1. Thundering Herd Test
        # Worker 1 Acquires
        w1_token = await mutex.acquire_node_lock(target_node, "worker-alpha")
        assert w1_token == "worker-alpha", "Initial acquisition failed."
        
        # Worker 2 Attempts concurrently and correctly receives Yield
        w2_token = await mutex.acquire_node_lock(target_node, "worker-beta")
        assert w2_token is None, "Thundering Herd breached! Mutual exclusion failed."
        print("Mutual Exclusion & Wait-Free Yielding Confirmed.")
        
        # 2. Lock Theft Shield Test (LUA Guard)
        # Force-expire Worker 1's lock in the mock state
        mutex._redis_mock_state[f"cg:lock:{target_node}"] = ("worker-alpha", time.time() - 10.0)
        
        # Worker 3 acquires the now-expired lock
        w3_token = await mutex.acquire_node_lock(target_node, "worker-gamma")
        assert w3_token == "worker-gamma", "Lock recovery of expired node failed."
        
        # Worker 1 wakes up and attempts to delete the lock (Must False)
        release_success = await mutex.release_node_lock(target_node, "worker-alpha")
        assert release_success is False, "LUA Shield Breached: Worker A stole Worker C's lock."
        print("LUA-Based Sovereignty Guard Confirmed.")
        
        # 3. Potato Tier Jitter Math
        potato_mutex = DistributedLockManager(tier="potato")
        jitter_1 = potato_mutex._calculate_backoff_jitter(attempt_count=1)
        jitter_2 = potato_mutex._calculate_backoff_jitter(attempt_count=2)
        assert jitter_2 > jitter_1, "Exponential backoff math failure."
        assert jitter_1 >= 1.0, "Potato backoff jitter is too aggressive (must be > 1.0s)."
        print("Potato Tier Jitter Calibration Confirmed.")

    asyncio.run(run_contention_gauntlet())
    print("--- DIAGNOSTIC COMPLETE: RELATIONAL INTEGRITY SECURE ---")
