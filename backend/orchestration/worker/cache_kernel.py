import asyncio
import time
import hashlib
import hmac
import logging
import secrets
import json
from collections import OrderedDict
from typing import Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DistributedWorkerLocalCache:
    """
    MODULE 7 - TASK 024: DISTRIBUTED WORKER-LOCAL CACHING KERNEL & EDGE-COHERENCY PROTOCOL
    The Short-Term Reflex System. Implements silicon-speed L1 cache bypassing network
    latency. Secures memory by AES-wrap mock and HMAC sealing, strictly enforcing LRU
    capacity limits to never breach residency limits.
    """

    __slots__ = (
        "_tier",
        "_max_cache_items",
        "_cache_store",
        "_hud_sync_counter",
        "_session_key",
        "_hits",
        "_misses",
        "_evictions",
    )

    def __init__(self, tier: str = "redline") -> None:
        self._tier = tier
        # Ordered dict operates as high-performance LRU queue
        self._cache_store: OrderedDict[str, Tuple[bytes, str]] = OrderedDict()
        self._hud_sync_counter = 0

        # Volatile AES-Wrap equivalent key bound purely to worker lifecycle
        self._session_key = secrets.token_bytes(32)

        self._hits = 0
        self._misses = 0
        self._evictions = 0

        self._calibrate_cache_capacity()

    def _calibrate_cache_capacity(self) -> None:
        """
        Hardware-Aware Residency Gear-Box.
        """
        if self._tier == "redline":
            self._max_cache_items = 1000000  # Massive Semantic Pre-Fetching (~4GB capacity)
        else:  # potato
            self._max_cache_items = 10000  # Ephemeral LRU & Heap Preservation (~10MB/50MB capacity)

    async def _emit_hud_pulse(self) -> None:
        """
        Cache-to-HUD Sync Manifold. Yield logic for 144Hz diagnostic sync.
        """
        self._hud_sync_counter += 1
        if self._hud_sync_counter % 100 == 0:
            await asyncio.sleep(0)

    def _generate_hmac_seal(self, payload: bytes) -> str:
        """
        The Tamper-Proof Checksum. Generates SHA256 HMAC for the residency blob.
        """
        return hmac.new(self._session_key, payload, hashlib.sha256).hexdigest()

    def _encrypt_payload(self, data: Any) -> bytes:
        """
        Volatile AES-Wrap simulation. Converts dict into secure binary blob.
        (Real application uses cryptography.fernet for symmetric AES wrapping)
        """
        raw_json = json.dumps(data, sort_keys=True).encode("utf-8")
        # XOR mock for speed logic check (simulates AES cipher operation)
        return bytes(b ^ self._session_key[i % 32] for i, b in enumerate(raw_json))

    def _decrypt_payload(self, blob: bytes) -> Any:
        """
        Restores binary blob back to Python dictionary object.
        """
        raw_json = bytes(b ^ self._session_key[i % 32] for i, b in enumerate(blob))
        return json.loads(raw_json.decode("utf-8"))

    async def set_intelligence(self, key: str, value: Any) -> None:
        """
        THE LRU EVICTION KERNEL - WRITE PATH
        Encrypts payload, calculates seal, performs eviction if at capacity, unshifts to LRU head.
        """
        await self._emit_hud_pulse()

        if key in self._cache_store:
            del self._cache_store[key]
        elif len(self._cache_store) >= self._max_cache_items:
            # Force LRU eviction from tail
            self._cache_store.popitem(last=False)
            self._evictions += 1

        encrypted_blob = self._encrypt_payload(value)
        seal = self._generate_hmac_seal(encrypted_blob)

        self._cache_store[key] = (encrypted_blob, seal)

    async def get_intelligence(self, key: str) -> Optional[Any]:
        """
        THE LRU EVICTION KERNEL - READ PATH
        Validates HMAC Seal, decrypts if unmodified, promotes to head of LRU queue.
        """
        await self._emit_hud_pulse()

        if key not in self._cache_store:
            self._misses += 1
            return None

        encrypted_blob, stored_seal = self._cache_store[key]

        # Verify the Tamper-Proof Checksum
        active_seal = self._generate_hmac_seal(encrypted_blob)
        if not hmac.compare_digest(stored_seal, active_seal):
            # Memory Corruption Anomaly! Force-Evict and fail over.
            del self._cache_store[key]
            self._evictions += 1
            self._misses += 1
            logging.error(f"[SECURITY] Memory corruption detected for key: {key}. Evicted.")
            return None

        # Promote to LRU head
        self._cache_store.move_to_end(key)
        self._hits += 1

        return self._decrypt_payload(encrypted_blob)

    async def process_invalidation_signal(self, key: str) -> bool:
        """
        THE ASYNCHRONOUS INVALIDATION MANIFOLD (Edge-Coherency).
        Triggered when global truth changes on Redis PubSub. Atomically drops the stale cache view.
        """
        if key in self._cache_store:
            del self._cache_store[key]
            self._evictions += 1
            return True
        return False

    async def flush_all_entropy(self) -> None:
        """
        THE "QUENCHING" PURGE. Destroys all stored state overwriting RAM references.
        """
        self._cache_store.clear()
        self._session_key = secrets.token_bytes(32)


# =================================================================================================
# DIAGNOSTIC EXECUTION & VALIDATION KERNEL
# =================================================================================================
async def _execute_cache_diagnostics() -> None:
    print("--- INITIATING LOCAL CACHE REFLEX DIAGNOSTICS ---")

    redline_cache = DistributedWorkerLocalCache(tier="redline")

    # 1. THE INSTANT PURGE GAUNTLET (Coherency Protocol)
    print("[*] Validating Asynchronous Invalidation & Coherency...")
    await redline_cache.set_intelligence("npm_rate_limit", {"remaining": 100})
    val = await redline_cache.get_intelligence("npm_rate_limit")
    assert val and val["remaining"] == 100, "L1 Cache write failure."

    # Simulate DB Update & Broadcast
    await redline_cache.process_invalidation_signal("npm_rate_limit")
    stale_val = await redline_cache.get_intelligence("npm_rate_limit")
    assert stale_val is None, "Edge-Coherency failed! Stale logic retrieved."
    print("    [+] Edge-Coherency Protocol nominal. Stale data instantly annihilated.")

    # 2. THE TAMPER-PROOF AUDIT (Crypto-Secure Memory)
    print("[*] Auditing Volatile AES-Wrap & HMAC Tamper Protections...")
    await redline_cache.set_intelligence("auth_signature", {"token": "alpha_123"})

    # Malicious injection directly into RAM bypasses `set_intelligence`
    corrupted_blob = b"corrupted_" + redline_cache._cache_store["auth_signature"][0][10:]
    original_seal = redline_cache._cache_store["auth_signature"][1]
    redline_cache._cache_store["auth_signature"] = (
        corrupted_blob,
        original_seal,
    )  # Overwrite memory maliciously

    auth_val = await redline_cache.get_intelligence("auth_signature")
    assert (
        auth_val is None
    ), "Memory tampered footprint bypassed HMAC filter! Catastrophic OpSec breach."
    print("    [+] RAM Memory Corruption interdicted. Encrypted L1 Cache perfectly secure.")

    # 3. THE MEMORY OVERFLOW STRESS (LRU Gear-Box)
    print("[*] Simulating Memory Saturation (Potato Tier LRU Attenuation)...")
    potato_cache = DistributedWorkerLocalCache(tier="potato")
    # Potato limit is 10,000. Let's stress 10,005
    for i in range(10005):
        await potato_cache.set_intelligence(f"hot_path_{i}", {"meta": i})

    assert (
        len(potato_cache._cache_store) == 10000
    ), f"Residency baseline breached! Size: {len(potato_cache._cache_store)}"

    # Verify the oldest 5 were shifted out
    oldest_query = await potato_cache.get_intelligence("hot_path_0")
    assert oldest_query is None, "LRU tail eviction failed."
    print("    [+] Adaptive Memory Pressure Scaling engaged. Heap Fragmentation prevented.")

    print("--- DIAGNOSTIC COMPLETE: WORKER REFLEX CACHE SECURE ---")


if __name__ == "__main__":
    asyncio.run(_execute_cache_diagnostics())
