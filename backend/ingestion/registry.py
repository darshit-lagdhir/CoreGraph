"""
Global Synchronicity, Mmap-backed Bloom Filter, and Frontier Management Kernel.
High-Density Existence Oracle and Batch Handshake Phalanx.
"""

import os
import mmap
import hashlib
import asyncio
from typing import Set, Dict, Any, Tuple


class ManifestRegistry:
    __slots__ = (
        "hardware_tier",
        "_registry_path",
        "_fd",
        "_mmap_filter",
        "_bf_size_bytes",
        "_bf_k_hashes",
        "_inflight_set",
        "_lock",
        "_counters",
    )

    def __init__(self, hardware_tier: str, registry_dir: str = "/tmp/coregraph_registry"):
        self.hardware_tier = hardware_tier
        self._inflight_set: Set[str] = set()
        self._lock = asyncio.Lock()

        self._counters: Dict[str, int] = {
            "discovered": 0,
            "processed": 0,
            "persisted": 0,
            "skipped": 0,
        }

        os.makedirs(registry_dir, exist_ok=True)
        self._registry_path = os.path.join(
            registry_dir, f"global_manifest_{self.hardware_tier}.bin"
        )

        if self.hardware_tier == "redline":
            self._bf_size_bytes = 256 * 1024 * 1024  # 256MB for ultra-low collision rate
            self._bf_k_hashes = 7
        elif self.hardware_tier == "potato":
            self._bf_size_bytes = 32 * 1024 * 1024  # 32MB for memory preservation
            self._bf_k_hashes = 5
        else:
            self._bf_size_bytes = 128 * 1024 * 1024
            self._bf_k_hashes = 6

        self._initialize_mmap()

    def _initialize_mmap(self) -> None:
        if not os.path.exists(self._registry_path):
            with open(self._registry_path, "wb") as f:
                f.write(b"\0" * self._bf_size_bytes)

        self._fd = os.open(self._registry_path, os.O_RDWR)
        self._mmap_filter = mmap.mmap(self._fd, self._bf_size_bytes, access=mmap.ACCESS_WRITE)

    def _get_hash_indices(self, item: str) -> Tuple[int, ...]:
        num_bits = self._bf_size_bytes * 8
        hashed = hashlib.md5(item.encode("utf-8")).digest()
        base_h1 = int.from_bytes(hashed[:8], "little")
        base_h2 = int.from_bytes(hashed[8:], "little")

        indices = []
        for i in range(self._bf_k_hashes):
            indices.append((base_h1 + i * base_h2) % num_bits)
        return tuple(indices)

    def _check_historical_existence(self, purl: str) -> bool:
        indices = self._get_hash_indices(purl)
        for idx in indices:
            byte_idx = idx // 8
            bit_idx = idx % 8
            if not (self._mmap_filter[byte_idx] & (1 << bit_idx)):
                return False
        return True

    def _set_historical_existence(self, purl: str) -> None:
        indices = self._get_hash_indices(purl)
        for idx in indices:
            byte_idx = idx // 8
            bit_idx = idx % 8
            self._mmap_filter[byte_idx] |= 1 << bit_idx

    async def check_existence(self, purl: str) -> str:
        """
        Returns 'SKIP' if globally processed or in-flight by another worker.
        Returns 'PROCESS' if untouched.
        """
        async with self._lock:
            if purl in self._inflight_set:
                self._counters["skipped"] += 1
                return "SKIP"

            if self._check_historical_existence(purl):
                self._counters["skipped"] += 1
                return "SKIP"

            return "PROCESS"

    async def report_discovery(self, purl: str) -> None:
        async with self._lock:
            self._inflight_set.add(purl)
            self._counters["discovered"] += 1

    async def mark_as_persisted(self, purl: str) -> None:
        async with self._lock:
            if purl in self._inflight_set:
                self._inflight_set.remove(purl)
            self._set_historical_existence(purl)
            self._counters["persisted"] += 1

    def calculate_batch_checksum(self) -> str:
        ctx = hashlib.sha256()
        ctx.update(str(self._counters["discovered"]).encode("utf-8"))
        ctx.update(str(self._counters["persisted"]).encode("utf-8"))

        # Mmap integrity hash sampling (reads first and last MB to prevent full I/O block)
        sample_size = min(1024 * 1024, self._bf_size_bytes)
        ctx.update(self._mmap_filter[:sample_size])
        ctx.update(self._mmap_filter[-sample_size:])

        return ctx.hexdigest()

    async def verify_relational_equilibrium(self) -> bool:
        """Wait-free sync block. Governor confirms if inflight matches persisted state."""
        async with self._lock:
            if len(self._inflight_set) > 0:
                return False
            # Check differential variance allowing minor skip drift
            discrepancy = (
                self._counters["discovered"]
                - self._counters["persisted"]
                - self._counters["skipped"]
            )
            return discrepancy <= 0

    def get_frontier_metrics(self) -> Dict[str, Any]:
        return {
            "discovered": self._counters["discovered"],
            "inflight_density": len(self._inflight_set),
            "persisted": self._counters["persisted"],
            "cache_hit_skips": self._counters["skipped"],
        }

    def _flush_mmap_to_disk(self) -> None:
        if hasattr(self, "_mmap_filter") and self._mmap_filter:
            self._mmap_filter.flush()

    def __del__(self):
        self._flush_mmap_to_disk()
        if hasattr(self, "_mmap_filter") and self._mmap_filter:
            self._mmap_filter.close()
        if hasattr(self, "_fd"):
            os.close(self._fd)
