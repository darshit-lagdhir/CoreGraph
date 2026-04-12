import asyncio
import time
import logging
import math
from typing import Dict, Any, Tuple, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DistributedRateLimitGovernor:
    """
    MODULE 7 - TASK 018: GLOBAL DISTRIBUTED RATE-LIMITING MANIFOLD & TOKEN-BUCKET SYNCHRONIZATION KERNEL
    Enforces registry diplomacy by wrapping extraction queries in an atomic token-bucket protocol.
    Provides hardware-aware leasing for high-latency workers (Potato) and microsecond arbitration
    for high-flow clusters, alongside a 429 self-healing throttling circuit.
    """

    __slots__ = (
        "_tier",
        "_global_registry_states",
        "_worker_lease_cache",
        "_hud_sync_counter",
        "_lease_size",
        "_quenching_windows",
    )

    def __init__(self, tier: str = "redline") -> None:
        self._tier = tier
        self._hud_sync_counter = 0

        # Mocking the Redis Atomic Datastore. Structure:
        # { "registry_id": {"tokens": float, "last_refill": float, "max_bucket": int, "refill_rate": float} }
        self._global_registry_states: Dict[str, Dict[str, Any]] = {}
        self._worker_lease_cache: Dict[str, Dict[str, int]] = {}
        self._quenching_windows: Dict[str, float] = {}

        self._calibrate_metabolic_pacing()

    def _calibrate_metabolic_pacing(self) -> None:
        """
        Hardware-Aware Lease Manifold Gear-Box.
        """
        if self._tier == "redline":
            self._lease_size = 1  # Microsecond Arbitration. Zero token-hoarding.
        else:  # potato
            self._lease_size = 10  # Batched Permissions. Lower Redis overhead.

    async def _emit_hud_pulse(self) -> None:
        """
        Metabolic-to-HUD Sync Manifold. Yields execution to maintain 144Hz render lock.
        """
        self._hud_sync_counter += 1
        if self._hud_sync_counter % 50 == 0:
            await asyncio.sleep(0)

    def register_registry_policy(
        self, registry_id: str, bucket_max: int, tokens_per_second: float
    ) -> None:
        """
        Seeds the internal atomic store with registry limits.
        """
        self._global_registry_states[registry_id] = {
            "tokens": float(bucket_max),
            "max_bucket": bucket_max,
            "refill_rate": tokens_per_second,
            "last_refill": time.time(),
        }

    async def _execute_atomic_lua_token_bucket(
        self, registry_id: str, current_time: float
    ) -> Tuple[bool, float, int]:
        """
        Mock implementation of the Redis LUA Token-Bucket.
        Calculates refill, asserts availability, and decrements atomically.
        Returns: (Is_Granted, Wait_ms_if_denied, Granted_Quantity)
        """
        await self._emit_hud_pulse()

        # Self-Healing Throttle: Check Quenching Window
        quench_expiry = self._quenching_windows.get(registry_id, 0.0)
        if current_time < quench_expiry:
            wait_time = quench_expiry - current_time
            return False, wait_time * 1000.0, 0

        state = self._global_registry_states.get(registry_id)
        if not state:
            return False, 1000.0, 0  # Unregistered policy default delay

        elapsed = current_time - state["last_refill"]
        refill_amount = elapsed * state["refill_rate"]

        # Temporal Refill Calculation
        state["tokens"] = min(float(state["max_bucket"]), state["tokens"] + refill_amount)
        state["last_refill"] = current_time

        # Sovereign Consumption Check
        required_tokens = min(self._lease_size, math.floor(state["tokens"]))

        if required_tokens >= 1:
            state["tokens"] -= required_tokens
            return True, 0.0, required_tokens
        else:
            # Calculate time until 1 token is available
            time_to_wait = (1.0 - state["tokens"]) / state["refill_rate"]
            return False, time_to_wait * 1000.0, 0

    async def acquire_registry_token(self, registry_id: str, worker_id: str) -> Dict[str, Any]:
        """
        The Master Arbitration entrypoint. Checks local lease cache first, then hits global atomic state.
        """
        current_time = time.time()

        # 1. Check Local Worker Lease Cache
        worker_cache = self._worker_lease_cache.setdefault(worker_id, {})
        if worker_cache.get(registry_id, 0) > 0:
            worker_cache[registry_id] -= 1
            return {"status": "proceed", "source": "local_lease", "wait_ms": 0.0}

        # 2. Execute Global LUA Arbitration
        is_granted, wait_ms, tokens_awarded = await self._execute_atomic_lua_token_bucket(
            registry_id, current_time
        )

        if is_granted:
            # If batching (Potato Tier), store remainder in cache
            if tokens_awarded > 1:
                worker_cache[registry_id] = tokens_awarded - 1

            return {"status": "proceed", "source": "brokered_lua", "wait_ms": 0.0}
        else:
            return {"status": "delayed", "source": "bucket_empty", "wait_ms": wait_ms}

    async def report_registry_hostility(self, registry_id: str, status_code: int) -> Dict[str, Any]:
        """
        The Adaptive Refill Decay Kernel.
        Intercepts 429 Too Many Requests to programmatically apply systemic retreat.
        """
        await self._emit_hud_pulse()

        if status_code == 429:
            state = self._global_registry_states.get(registry_id)
            if state:
                # 1. Halve the Refill Rate
                original_rate = state["refill_rate"]
                state["refill_rate"] = max(0.1, original_rate * 0.5)

                # 2. Trigger Global Quenching Window (e.g., 60 seconds of complete silence)
                quench_time = 60.0
                self._quenching_windows[registry_id] = time.time() + quench_time

                # Invalidate all local cached leases across workers
                for w in self._worker_lease_cache.values():
                    if registry_id in w:
                        w[registry_id] = 0

                return {
                    "status": "hostility_quenched",
                    "old_rate": original_rate,
                    "new_rate": state["refill_rate"],
                    "quench_duration_s": quench_time,
                }

        return {"status": "no_action_required"}


# =================================================================================================
# DIAGNOSTIC EXECUTION & VALIDATION KERNEL
# =================================================================================================
async def _execute_metabolic_diagnostics() -> None:
    print("--- INITIATING METABOLIC REGULATION DIAGNOSTICS ---")

    redline_gov = DistributedRateLimitGovernor(tier="redline")

    # Register Github Policy (Mock): Max 10 burst, refill 5 per second
    redline_gov.register_registry_policy("github_api", bucket_max=10, tokens_per_second=5.0)

    # 1. THE THUNDERING HERD GAUNTLET (Token Saturation)
    print("[*] Validating Global Atomic Rate-Limit Enforcement...")
    approved = 0
    delayed = 0
    # Simulate 15 parallel requests hitting a bucket of 10
    for i in range(15):
        res = await redline_gov.acquire_registry_token("github_api", f"worker_{i}")
        if res["status"] == "proceed":
            approved += 1
        else:
            delayed += 1

    assert approved == 10, f"Thundering herd bypassed the shield! Approved: {approved}"
    assert delayed == 5, f"Delay metric off. Delayed: {delayed}"
    print("    [+] LUA Atomic Arbitration successful. Network extraction perfectly paced.")

    # 2. REGISTRY BLACKOUT RECOVERY (429 Shield)
    print("[*] Simulating HTTP 429 Error & Systematic Retreat Protocol...")
    hostility_res = await redline_gov.report_registry_hostility("github_api", 429)
    assert hostility_res["status"] == "hostility_quenched"
    assert hostility_res["new_rate"] == 2.5, "Refill rate failed to decay by 50%."

    # Assert Quench Window blocks immediate retries
    quench_res = await redline_gov.acquire_registry_token("github_api", "worker_1")
    assert quench_res["status"] == "delayed", "Quenching window failed. Token erroneously granted."
    assert quench_res["wait_ms"] > 50000.0, "Wait time does not reflect the 60s quench blackout."
    print(
        "    [+] Systematic Retreat Protocol active. 60s blackout engaged, refill trajectory halved."
    )

    # 3. POTATO TIER LEASING BENCHMARK
    print("[*] Auditing Potato Tier Batch-Leasing Architecture...")
    potato_gov = DistributedRateLimitGovernor(tier="potato")
    potato_gov.register_registry_policy("npm_registry", bucket_max=100, tokens_per_second=10.0)

    # Potato worker requests token. It should receive its batch constraint (10 in this mock).
    p_worker = "potato_alpha"
    lease_res = await potato_gov.acquire_registry_token("npm_registry", p_worker)
    assert lease_res["status"] == "proceed", "Lease denied."

    # Check if subsequent calls use the cache, avoiding networking
    cache_res = await potato_gov.acquire_registry_token("npm_registry", p_worker)
    assert cache_res["source"] == "local_lease", "Worker failed to utilize local token cache."
    assert (
        potato_gov._worker_lease_cache[p_worker]["npm_registry"] == 8
    ), "Lease count subtraction failed."
    print(
        "    [+] Batched Token Leases operational. Network I/O drastically minimized for legacy hardware."
    )

    print("--- DIAGNOSTIC COMPLETE: METABOLIC KERNEL SECURE ---")


if __name__ == "__main__":
    asyncio.run(_execute_metabolic_diagnostics())
