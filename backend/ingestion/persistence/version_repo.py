"""
Chronological Atomicity, B-Tree Index Efficiency, and Relational Integrity Kernel.
High-Density Asynchronous Temporal Materialization Phalanx.
"""

import asyncio
import time
import random
from typing import List, Tuple, Dict, Any


class VersionPersistenceRepository:
    __slots__ = (
        "hardware_tier",
        "_pool",
        "_version_buffer",
        "_chunk_limit",
        "_max_retries",
        "_backpressure_flag",
        "_telemetry",
        "_db_concurrency_semaphore",
    )

    VERSION_UPSERT_SQL = """
        INSERT INTO versions (package_id, version_index, version_string, timestamp, license, forensic_signature, risk_flags)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (package_id, version_string) DO UPDATE SET
            risk_flags = EXCLUDED.risk_flags,
            forensic_signature = EXCLUDED.forensic_signature,
            last_observed = CURRENT_TIMESTAMP
    """

    LATEST_VERSION_UPDATE_SQL = """
        UPDATE packages
        SET latest_version = $2
        WHERE id = $1 AND (latest_version_index IS NULL OR latest_version_index < $3)
    """

    def __init__(self, hardware_tier: str, pool: Any):
        self.hardware_tier = hardware_tier
        self._pool = pool
        self._version_buffer: List[Tuple] = []
        self._max_retries = 3
        self._backpressure_flag = False

        if self.hardware_tier == "redline":
            self._chunk_limit = 5000
            self._db_concurrency_semaphore = asyncio.Semaphore(4)
        elif self.hardware_tier == "potato":
            self._chunk_limit = 1000
            self._db_concurrency_semaphore = asyncio.Semaphore(1)
        else:
            self._chunk_limit = 2500
            self._db_concurrency_semaphore = asyncio.Semaphore(2)

        self._telemetry: Dict[str, Any] = {
            "versions_materialized": 0,
            "index_latency_ms": 0.0,
            "flush_count": 0,
            "deadlocks_recovered": 0,
        }

    async def add_version_record(self, data: Tuple) -> None:
        self._version_buffer.append(data)

        if len(self._version_buffer) >= self._chunk_limit:
            await self._flush_versions()

    def _optimize_temporal_order(self, records: List[Tuple]) -> List[Tuple]:
        # Tuple format expected: (pkg_id, v_index, v_string, timestamp, license, sig, risk)
        return sorted(records, key=lambda x: (x[0], x[1]))

    async def _flush_versions(self, force: bool = False) -> None:
        if not self._version_buffer and not force:
            return

        batch_to_flush = self._optimize_temporal_order(self._version_buffer.copy())
        self._version_buffer.clear()

        if not batch_to_flush:
            return

        start_time = time.perf_counter()

        async with self._db_concurrency_semaphore:
            await self._execute_transaction(batch_to_flush)

        latency = (time.perf_counter() - start_time) * 1000
        self._update_telemetry(len(batch_to_flush), latency)

        if self.hardware_tier == "potato":
            await asyncio.sleep(0.05)

    async def _execute_transaction(self, records: List[Tuple]) -> None:
        for attempt in range(self._max_retries):
            try:
                if hasattr(self._pool, "acquire"):
                    async with self._pool.acquire() as connection:
                        async with connection.transaction(isolation="read_committed"):
                            await connection.executemany(self.VERSION_UPSERT_SQL, records)

                            # Calculate Latest Version Delta per-batch to prevent DB strain
                            latest_map = {}
                            for r in records:
                                pkg_id, v_idx, v_str = r[0], r[1], r[2]
                                if pkg_id not in latest_map or v_idx > latest_map[pkg_id][1]:
                                    latest_map[pkg_id] = (v_str, v_idx)

                            latest_updates = [
                                (pid, val[0], val[1]) for pid, val in latest_map.items()
                            ]
                            if latest_updates:
                                await connection.executemany(
                                    self.LATEST_VERSION_UPDATE_SQL, latest_updates
                                )
                return
            except Exception as e:
                err_str = str(e).lower()
                if "deadlock" in err_str or "serialization" in err_str:
                    self._telemetry["deadlocks_recovered"] += 1
                    if attempt < self._max_retries - 1:
                        jitter = (0.1 * (2**attempt)) + random.uniform(0.01, 0.05)
                        await asyncio.sleep(jitter)
                        continue
                raise e

    def _update_telemetry(self, record_count: int, latency_ms: float) -> None:
        self._telemetry["versions_materialized"] += record_count

        current_avg = self._telemetry["index_latency_ms"]
        flush_count = self._telemetry["flush_count"]

        new_avg = ((current_avg * flush_count) + latency_ms) / (flush_count + 1)

        self._telemetry["index_latency_ms"] = new_avg
        self._telemetry["flush_count"] += 1

        threshold = 200 if self.hardware_tier == "redline" else 600
        self._backpressure_flag = latency_ms > threshold

    def is_backpressured(self) -> bool:
        return self._backpressure_flag

    def get_telemetry(self) -> Dict[str, Any]:
        return self._telemetry.copy()
