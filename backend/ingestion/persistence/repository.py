"""
Transactional Atomicity, Write-Ahead Log Efficiency, and Relational Integrity Kernel.
High-Density Asynchronous Upsert Phalanx.
"""

import asyncio
import time
import random
from typing import List, Tuple, Dict, Any, Optional


class PersistenceRepository:
    __slots__ = (
        "hardware_tier",
        "_pool",
        "_node_buffer",
        "_edge_buffer",
        "_chunk_limit",
        "_max_retries",
        "_backpressure_flag",
        "_telemetry",
        "_db_concurrency_semaphore",
    )

    NODE_UPSERT_SQL = """
        INSERT INTO nodes (purl, name, version, risk_flags, forensic_signature)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (purl) DO UPDATE SET
            risk_flags = EXCLUDED.risk_flags,
            forensic_signature = EXCLUDED.forensic_signature,
            last_observed = CURRENT_TIMESTAMP
    """

    EDGE_UPSERT_SQL = """
        INSERT INTO edges (source, target, requirement)
        VALUES ($1, $2, $3)
        ON CONFLICT (source, target) DO UPDATE SET
            requirement = EXCLUDED.requirement,
            last_observed = CURRENT_TIMESTAMP
    """

    def __init__(self, hardware_tier: str, pool: Any):
        self.hardware_tier = hardware_tier
        self._pool = pool
        self._node_buffer: List[Tuple] = []
        self._edge_buffer: List[Tuple] = []
        self._backpressure_flag = False
        self._max_retries = 3

        if self.hardware_tier == "redline":
            self._chunk_limit = 5000
            self._db_concurrency_semaphore = asyncio.Semaphore(4)
        elif self.hardware_tier == "potato":
            self._chunk_limit = 500
            self._db_concurrency_semaphore = asyncio.Semaphore(1)
        else:
            self._chunk_limit = 1000
            self._db_concurrency_semaphore = asyncio.Semaphore(2)

        self._telemetry: Dict[str, Any] = {
            "nodes_committed": 0,
            "edges_committed": 0,
            "transaction_latency_ms": 0.0,
            "flush_count": 0,
            "deadlocks_recovered": 0,
        }

    async def add_record(self, node: Optional[Tuple] = None, edge: Optional[Tuple] = None) -> None:
        if node:
            self._node_buffer.append(node)
        if edge:
            self._edge_buffer.append(edge)

        if (
            len(self._node_buffer) >= self._chunk_limit
            or len(self._edge_buffer) >= self._chunk_limit
        ):
            await self._flush_batch()

    async def _flush_batch(self) -> None:
        nodes_to_flush = self._node_buffer.copy()
        edges_to_flush = self._edge_buffer.copy()
        self._node_buffer.clear()
        self._edge_buffer.clear()

        if not nodes_to_flush and not edges_to_flush:
            return

        if not self._validate_batch_integrity(nodes_to_flush, edges_to_flush):
            return

        start_time = time.perf_counter()

        async with self._db_concurrency_semaphore:
            await self._execute_transaction(nodes_to_flush, edges_to_flush)

        latency = (time.perf_counter() - start_time) * 1000
        self._update_telemetry(len(nodes_to_flush), len(edges_to_flush), latency)

        if self.hardware_tier == "potato":
            await asyncio.sleep(0.05)

    async def _execute_transaction(self, nodes: List[Tuple], edges: List[Tuple]) -> None:
        for attempt in range(self._max_retries):
            try:
                if hasattr(self._pool, "acquire"):
                    async with self._pool.acquire() as connection:
                        async with connection.transaction(isolation="read_committed"):
                            if nodes:
                                await connection.executemany(self.NODE_UPSERT_SQL, nodes)
                            if edges:
                                await connection.executemany(self.EDGE_UPSERT_SQL, edges)
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

    def _validate_batch_integrity(self, nodes: List[Tuple], edges: List[Tuple]) -> bool:
        for node in nodes:
            if not isinstance(node[0], str) or len(node[0]) == 0:
                return False

        for edge in edges:
            if not isinstance(edge[0], str) or not isinstance(edge[1], str):
                return False

        return True

    def _update_telemetry(self, node_count: int, edge_count: int, latency_ms: float) -> None:
        self._telemetry["nodes_committed"] += node_count
        self._telemetry["edges_committed"] += edge_count

        current_avg = self._telemetry["transaction_latency_ms"]
        flush_count = self._telemetry["flush_count"]

        new_avg = ((current_avg * flush_count) + latency_ms) / (flush_count + 1)

        self._telemetry["transaction_latency_ms"] = new_avg
        self._telemetry["flush_count"] += 1

        if latency_ms > (100 if self.hardware_tier == "redline" else 400):
            self._backpressure_flag = True
        else:
            self._backpressure_flag = False

    def is_backpressured(self) -> bool:
        return self._backpressure_flag

    def get_telemetry(self) -> Dict[str, Any]:
        return self._telemetry.copy()
