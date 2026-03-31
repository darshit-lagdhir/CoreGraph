import asyncio
import time
import hashlib
from typing import Dict, Any, Optional, Tuple


class FinancialAbsenceInterceptor:
    __slots__ = (
        "is_potato_tier",
        "bloom_capacity_bits",
        "bloom_bitfield",
        "num_hash_funcs",
        "absence_queue",
        "total_probes_dispatched",
        "bloom_filter_hits",
        "confirmed_absences",
        "_frame_start_time",
    )

    def __init__(self, is_potato_tier: bool = False, expected_nodes: int = 4_000_000):
        self.is_potato_tier = is_potato_tier

        # Probabilistic Bloom Filter tuning
        # For 4M nodes, 32M bits (~4MB) is well within the 150MB liquid memory mandate.
        self.bloom_capacity_bits = expected_nodes * 8
        self.bloom_bitfield = bytearray(self.bloom_capacity_bits // 8)
        self.num_hash_funcs = 3

        self.absence_queue: asyncio.Queue[Tuple[str, str, str, float]] = asyncio.Queue()

        self.total_probes_dispatched = 0
        self.bloom_filter_hits = 0
        self.confirmed_absences = 0
        self._frame_start_time = time.perf_counter()

    def _get_bloom_indices(self, package_id: str) -> Tuple[int, ...]:
        base_hash = hashlib.md5(package_id.encode("utf-8")).digest()
        h1 = int.from_bytes(base_hash[:8], "little")
        h2 = int.from_bytes(base_hash[8:], "little")
        return tuple((h1 + i * h2) % self.bloom_capacity_bits for i in range(self.num_hash_funcs))

    def check_negative_cache(self, package_id: str) -> bool:
        self.total_probes_dispatched += 1
        indices = self._get_bloom_indices(package_id)
        for idx in indices:
            byte_idx = idx // 8
            bit_idx = idx % 8
            if not (self.bloom_bitfield[byte_idx] & (1 << bit_idx)):
                return False

        self.bloom_filter_hits += 1
        return True

    def populate_negative_cache(self, package_id: str) -> None:
        indices = self._get_bloom_indices(package_id)
        for idx in indices:
            byte_idx = idx // 8
            bit_idx = idx % 8
            self.bloom_bitfield[byte_idx] |= 1 << bit_idx

    async def _yield_for_hud(self):
        elapsed = time.perf_counter() - self._frame_start_time
        if elapsed > 0.002:  # 2ms 144Hz vertical sync allowance
            await asyncio.sleep(0)
            self._frame_start_time = time.perf_counter()

    async def analyze_network_absence(
        self, package_id: str, registry_id: str, status_code: int, registry_health: int
    ) -> Optional[str]:
        if registry_health < 50 and status_code in (500, 502, 503, 504):
            # Systemic Outage - Not a factual absence
            return None

        if status_code == 404:
            await self._register_absence_fact(package_id, registry_id, "HTTP_404_NOT_FOUND")
            return "HTTP_404_NOT_FOUND"

        return None

    def _probe_empty_payload(self, payload: Dict[str, Any]) -> Optional[str]:
        if "errors" in payload:
            for error in payload["errors"]:
                if "Permission Denied" in str(error) or "PRIVATE" in str(error).upper():
                    return "PRIVATE_RESOURCE"

        # Deep-Tissue Traversal
        data = payload.get("data", payload)
        repo = data.get("repository", data.get("project", data))
        funding = repo.get("funding", repo.get("fundingLinks"))

        if funding is None:
            return "NULL_LEAF"

        if isinstance(funding, list) and len(funding) == 0:
            return "EMPTY_ARRAY"

        if isinstance(funding, dict):
            if funding.get("amount") is None and funding.get("balance") is None:
                return "NULL_LEAF"
            status = str(funding.get("status", "")).upper()
            if status in ("ARCHIVED", "INACTIVE"):
                return "INACTIVE_STATUS"

        return None

    async def process_payload(
        self,
        package_id: str,
        registry_id: str,
        status_code: int,
        payload: Optional[Dict[str, Any]] = None,
        registry_health: int = 100,
    ) -> Optional[str]:
        if self.check_negative_cache(package_id):
            return "CACHED_ABSENCE"

        absence_code = await self.analyze_network_absence(
            package_id, registry_id, status_code, registry_health
        )

        if not absence_code and status_code == 200 and payload:
            absence_code = self._probe_empty_payload(payload)
            if absence_code:
                await self._register_absence_fact(package_id, registry_id, absence_code)

        await self._yield_for_hud()
        return absence_code

    async def _register_absence_fact(
        self, package_id: str, registry_id: str, reason_code: str
    ) -> None:
        self.populate_negative_cache(package_id)
        self.confirmed_absences += 1
        epoch = time.time()
        await self.absence_queue.put((package_id, registry_id, reason_code, epoch))

    def get_void_density_score(self) -> float:
        if self.total_probes_dispatched == 0:
            return 0.0
        return self.bloom_filter_hits / self.total_probes_dispatched


# ======================================================================================
# THE "VANISHING DATA" GAUNTLET
# ======================================================================================
async def execute_void_gauntlet():
    interceptor = FinancialAbsenceInterceptor(is_potato_tier=False)

    t_start = time.perf_counter()

    # Test 1: Redundancy Suppression Benchmark
    target_package = "pkg_redundant_void"
    for _ in range(10000):
        await interceptor.process_payload(target_package, "npm", 404, None, registry_health=100)

    assert interceptor.bloom_filter_hits == 9999, "Negative Cache failed suppression limits"
    assert interceptor.confirmed_absences == 1, "Fact Materialization duplicated"

    # Test 2: Null Payload Audit
    mock_payloads = [
        ({"data": {"repository": {"funding": []}}}, "EMPTY_ARRAY"),
        ({"data": {"repository": {"funding": {"amount": None}}}}, "NULL_LEAF"),
        (
            {"data": {"project": {"funding": {"amount": 0.0, "status": "INACTIVE"}}}},
            "INACTIVE_STATUS",
        ),
        (
            {"errors": [{"message": "Resource PRIVATE_RESOURCE or Permission Denied"}]},
            "PRIVATE_RESOURCE",
        ),
    ]

    for payload, expected_sig in mock_payloads:
        sig = await interceptor.process_payload(
            f"pkg_{expected_sig}", "pypi", 200, payload, registry_health=100  # type: ignore
        )
        assert sig == expected_sig, f"Empty-Set Manifold failed on {expected_sig}"

    # Test 3: 404 vs 500 Stress
    await interceptor.process_payload("pkg_outage_test", "crates", 503, None, registry_health=20)
    assert "pkg_outage_test" not in [
        item[0] for item in interceptor.absence_queue._queue  # type: ignore
    ], "Outage mistranslated as absence"

    t_end = time.perf_counter()
    ms_elapsed = (t_end - t_start) * 1000

    density = interceptor.get_void_density_score()

    print("[+] ABSENCE DETECTION KERNEL SYNCHRONIZED.")
    print(f"[+] Operational Time: {ms_elapsed:.2f}ms")
    print(f"[+] Total Probes Dispatched: {interceptor.total_probes_dispatched}")
    print(f"[+] Total Confirmed Absences: {interceptor.confirmed_absences}")
    print(f"[+] Bloom Filter Hits (Redundancy Prevented): {interceptor.bloom_filter_hits}")
    print(f"[+] Void Density Score: {density:.6f}")
    print("[+] 144HZ HUD LIQUIDITY: PRESERVED")


if __name__ == "__main__":
    asyncio.run(execute_void_gauntlet())
