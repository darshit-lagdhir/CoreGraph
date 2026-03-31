"""
Topological Atomicity, Adjacency Index Efficiency, and Relational Consistency Kernel.
High-Density Asynchronous Edge Materialization Phalanx.
"""

import asyncio
import time
import random
from typing import List, Tuple, Dict, Any


class LinkageRepository:
    __slots__ = (
        "hardware_tier",
        "_pool",
        "_edge_buffer",
        "_pending_edges",
        "_chunk_limit",
        "_max_retries",
        "_backpressure_flag",
        "_telemetry",
        "_db_concurrency_semaphore",
    )

    LINKAGE_UPSERT_SQL = """
        INSERT INTO edges (source, target, requirement)
        VALUES ($1, $2, $3)
        ON CONFLICT (source, target) DO NOTHING
    """

    def __init__(self, hardware_tier: str, pool: Any):
        self.hardware_tier = hardware_tier
        self._pool = pool
        self._edge_buffer: List[Tuple] = []
        self._pending_edges: List[Tuple] = []
        self._max_retries = 3
        self._backpressure_flag = False

        if self.hardware_tier == "redline":
            self._chunk_limit = 10000
            self._db_concurrency_semaphore = asyncio.Semaphore(4)
        elif self.hardware_tier == "potato":
            self._chunk_limit = 2000
            self._db_concurrency_semaphore = asyncio.Semaphore(1)
        else:
            self._chunk_limit = 5000
            self._db_concurrency_semaphore = asyncio.Semaphore(2)

        self._telemetry: Dict[str, Any] = {
            "edges_materialized": 0,
            "index_latency_ms": 0.0,
            "stashed_edges": 0,
            "reconciled_edges": 0,
            "orphaned_edges": 0,
            "flush_count": 0,
        }

    async def add_link(self, edge: Tuple) -> None:
        if not isinstance(edge[0], str) or not isinstance(edge[1], str) or edge[0] == edge[1]:
            return  # Drop malformed or immediately self-referencing topological cycles

        self._edge_buffer.append(edge)

        if len(self._edge_buffer) >= self._chunk_limit:
            await self._flush_linkage()

    def _optimize_buffer(self, edges: List[Tuple]) -> List[Tuple]:
        return sorted(edges, key=lambda x: (x[0], x[1]))

    async def _flush_linkage(self, force: bool = False) -> None:
        if not self._edge_buffer and not force:
            return

        links_to_flush = self._optimize_buffer(self._edge_buffer.copy())
        self._edge_buffer.clear()

        if not links_to_flush:
            return

        start_time = time.perf_counter()

        async with self._db_concurrency_semaphore:
            success = await self._execute_transaction(links_to_flush)

        if not success:
            self._pending_edges.extend(links_to_flush)
            self._telemetry["stashed_edges"] += len(links_to_flush)
        else:
            self._telemetry["edges_materialized"] += len(links_to_flush)

        latency = (time.perf_counter() - start_time) * 1000
        self._update_telemetry(latency)

        if self.hardware_tier == "potato":
            await asyncio.sleep(0.05)

    async def _execute_transaction(self, edges: List[Tuple]) -> bool:
        for attempt in range(self._max_retries):
            try:
                if hasattr(self._pool, "acquire"):
                    async with self._pool.acquire() as connection:
                        async with connection.transaction(isolation="read_committed"):
                            await connection.executemany(self.LINKAGE_UPSERT_SQL, edges)
                return True
            except Exception as e:
                err_str = str(e).lower()
                if "deadlock" in err_str or "serialization" in err_str:
                    if attempt < self._max_retries - 1:
                        jitter = (0.1 * (2**attempt)) + random.uniform(0.01, 0.05)
                        await asyncio.sleep(jitter)
                        continue
                elif "foreign key" in err_str or "23503" in err_str:
                    return False
                raise e
        return False

    async def reconcile_pending_edges(self) -> None:
        if not self._pending_edges:
            return

        retry_batch = self._optimize_buffer(self._pending_edges.copy())
        self._pending_edges.clear()

        for edge in retry_batch:
            success = await self._execute_single(edge)
            if success:
                self._telemetry["edges_materialized"] += 1
                self._telemetry["reconciled_edges"] += 1
            else:
                self._telemetry["orphaned_edges"] += 1

    async def _execute_single(self, edge: Tuple) -> bool:
        try:
            if hasattr(self._pool, "acquire"):
                async with self._pool.acquire() as connection:
                    async with connection.transaction(isolation="read_committed"):
                        await connection.execute(self.LINKAGE_UPSERT_SQL, edge[0], edge[1], edge[2])
            return True
        except Exception as e:
            err_str = str(e).lower()
            if "foreign key" in err_str or "23503" in err_str:
                return False
        return False

    def _update_telemetry(self, latency_ms: float) -> None:
        current_avg = self._telemetry["index_latency_ms"]
        flush_count = self._telemetry["flush_count"]

        new_avg = ((current_avg * flush_count) + latency_ms) / (flush_count + 1)

        self._telemetry["index_latency_ms"] = new_avg
        self._telemetry["flush_count"] += 1

        threshold = 150 if self.hardware_tier == "redline" else 500
        self._backpressure_flag = latency_ms > threshold

    def is_backpressured(self) -> bool:
        return self._backpressure_flag

    def get_telemetry(self) -> Dict[str, Any]:
        stashed = self._telemetry["stashed_edges"]
        reconciled = self._telemetry["reconciled_edges"]
        rec_ratio = (reconciled / stashed) * 100 if stashed > 0 else 100.0

        metrics = self._telemetry.copy()
        metrics["reconciliation_ratio"] = round(rec_ratio, 2)
        return metrics
