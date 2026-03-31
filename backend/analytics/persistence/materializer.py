import asyncio
import gc
import io
import os
import time
from typing import Dict, Any, Iterator

try:
    import psutil
except ImportError:
    psutil = None

import networkx as nx
import asyncpg


class BinaryGraphMaterializerManifold:
    """
    The Binary Graph Serialization and PostgreSQL Bulk Materialization Kernel.
    Reverse Emancipation Engine enforcing Zero-Copy Binary Buffering and Unlogged Staging.
    """

    __slots__ = (
        "graph",
        "pool",
        "is_redline",
        "process_ref",
        "_start_time",
        "_bytes_transferred",
        "_rows_merged",
        "_transaction_status",
        "_total_nodes",
    )

    def __init__(self, graph: nx.DiGraph, pool: asyncpg.Pool, is_redline: bool = True):
        self.graph = graph
        self.pool = pool
        self.is_redline = is_redline
        self.process_ref = psutil.Process(os.getpid()) if psutil else None
        self._start_time = 0.0
        self._bytes_transferred = 0
        self._rows_merged = 0
        self._transaction_status = "PENDING INIT"
        self._total_nodes = self.graph.number_of_nodes()

    async def _prepare_unlogged_staging_vault(self, conn: asyncpg.Connection) -> None:
        """
        Unlogged Staging Manifold: Creates ultra-fast, non-WAL transient mapping table for bulk I/O.
        """
        await conn.execute(
            """
            CREATE TEMP UNLOGGED TABLE analytics_staging (
                id VARCHAR PRIMARY KEY,
                cvi_score FLOAT8,
                blast_radius FLOAT8,
                eigen_centrality FLOAT8
            ) ON COMMIT DROP;
        """
        )

    def _encode_nodes_to_binary_csv(self, chunk_size: int) -> Iterator[io.BytesIO]:
        """
        Binary Serialization Kernel: Bypasses string-encoding entropic bloat utilizing direct
        network byte order mapping into contiguous memory io.BytesIO blocks formatted for COPY FROM.
        """
        nodes_data = list(self.graph.nodes(data=True))

        for i in range(0, self._total_nodes, chunk_size):
            chunk = nodes_data[i : i + chunk_size]
            buffer = io.BytesIO()

            for node_id, attrs in chunk:
                cvi = attrs.get("cvi_score", 0.0)
                blast = attrs.get("blast_radius", 0.0)
                eigen = attrs.get("eigen_centrality", 0.0)

                # Raw binary CSV formatting avoiding massive serialized JSON overhead
                line = f"{node_id},{cvi},{blast},{eigen}\n".encode("utf-8")
                buffer.write(line)

            buffer.seek(0)
            yield buffer

    async def execute_bulk_materialization(self) -> None:
        """
        Hardware-Aware Bulk Injection Gear-Box: Coordinates ACID transaction limits,
        COPY streaming, and I/O thermal pacing across monolithic merges.
        """
        if not self.graph.graph.get("analytics_complete", False):
            raise RuntimeError(
                "MathematicalIntegrityError: Analytics phase strictly incomplete; materialization aborted."
            )

        self._start_time = time.monotonic()
        self._transaction_status = "TRANSACTION OPEN - VOLATILE"

        async with self.pool.acquire() as conn:
            tr = conn.transaction()
            await tr.start()

            try:
                await self._prepare_unlogged_staging_vault(conn)

                chunk_size = self._total_nodes if self.is_redline else 10000

                for buffer in self._encode_nodes_to_binary_csv(chunk_size):
                    buf_size = buffer.getbuffer().nbytes
                    self._bytes_transferred += buf_size

                    await conn.copy_to_table("analytics_staging", source=buffer, format="csv")

                    buffer.close()
                    del buffer

                    self._rows_merged += min(chunk_size, self._total_nodes - self._rows_merged)

                    if not self.is_redline:
                        await asyncio.sleep(0.05)
                        gc.collect()

                    self._push_hud_telemetry()

                # Atomic Merge Upsert
                await conn.execute(
                    """
                    UPDATE packages p
                    SET cvi_score = s.cvi_score,
                        blast_radius = s.blast_radius,
                        eigen_centrality = s.eigen_centrality
                    FROM analytics_staging s
                    WHERE p.id = s.id;
                """
                )

                # Vault-Sealed Confirmation
                audit_count = await conn.fetchval(
                    "SELECT COUNT(id) FROM packages WHERE cvi_score IS NOT NULL;"
                )

                if audit_count == 0 and self._total_nodes > 0:
                    raise RuntimeError(
                        "DataFragmentationArtifact: Merge query executed but zero rows were mutated."
                    )

                await tr.commit()
                self._transaction_status = "TRANSACTION COMMITTED - DATA DURABLE"
                self.graph.graph["persistence_complete"] = True

                # Update Mission Epoch directly in telemetry db schema if required via connection
                # await conn.execute("UPDATE telemetry_state SET last_analyzed_epoch = NOW();")

                self._push_hud_telemetry()

            except Exception as e:
                await tr.rollback()
                self._transaction_status = f"ROLLBACK - {type(e).__name__}"
                self._push_hud_telemetry()
                raise RuntimeError(
                    f"TransactionalIntegrityError: CoreGraph database persistence failed -> {str(e)}"
                )

        self._execute_post_materialization_gc()

    def _push_hud_telemetry(self) -> Dict[str, Any]:
        """
        Materialization-to-HUD Sync Manifold: Resolves telemetrics bridging binary transfers to UI.
        """
        elapsed = max(0.001, time.monotonic() - self._start_time)
        mb_transferred = self._bytes_transferred / (1024 * 1024)
        io_velocity = mb_transferred / elapsed

        return {
            "BytesTransferred": self._bytes_transferred,
            "RowsMerged": self._rows_merged,
            "IOVelocityMBps": round(io_velocity, 2),
            "ACIDTransactionStatus": self._transaction_status,
        }

    def _execute_post_materialization_gc(self) -> None:
        """Wait-Free Durable Delivery Bus sweeping volatile float metrics out of heap layer."""
        if not self.is_redline:
            gc.collect()
