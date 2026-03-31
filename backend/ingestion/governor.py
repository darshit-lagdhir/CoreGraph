import asyncio
import time
from typing import AsyncGenerator, Dict, List, Set, Any, Optional


class IngestionGovernor:
    __slots__ = (
        "hardware_tier",
        "concurrency_limit",
        "batch_size",
        "q_size",
        "input_queue",
        "output_queue",
        "batch_registry",
        "quarantined_nodes",
        "phalanx_tasks",
        "flusher_task",
        "tuner_task",
        "_is_running",
        "_total_processed",
        "_start_time",
        "_error_count",
        "_registry_client",
        "_parser_kernel",
        "_persistence_beast",
    )

    def __init__(
        self, hardware_tier: str, registry_client: Any, parser_kernel: Any, persistence_beast: Any
    ):
        self.hardware_tier = hardware_tier
        self._registry_client = registry_client
        self._parser_kernel = parser_kernel
        self._persistence_beast = persistence_beast

        if self.hardware_tier == "redline":
            self.concurrency_limit = 48
            self.batch_size = 5000
            self.q_size = 10000
        else:
            self.concurrency_limit = 4
            self.batch_size = 250
            self.q_size = 1000

        self.input_queue: asyncio.Queue = asyncio.Queue(maxsize=self.q_size)
        self.output_queue: asyncio.Queue = asyncio.Queue(maxsize=self.q_size)

        self.batch_registry: Dict[str, str] = {}
        self.quarantined_nodes: Set[str] = set()

        self.phalanx_tasks: List[asyncio.Task] = []
        self.flusher_task: Optional[asyncio.Task] = None
        self.tuner_task: Optional[asyncio.Task] = None

        self._is_running = False
        self._total_processed = 0
        self._start_time = 0.0
        self._error_count = 0

    async def start_phalanx(self, package_ids: AsyncGenerator[str, None]) -> None:
        self._is_running = True
        self._start_time = time.monotonic()

        self.flusher_task = asyncio.create_task(self._persistence_flusher())
        self.tuner_task = asyncio.create_task(self._tune_performance())

        for _ in range(self.concurrency_limit):
            task = asyncio.create_task(self._worker_loop())
            self.phalanx_tasks.append(task)

        async for pkg_id in package_ids:
            if pkg_id in self.quarantined_nodes:
                continue
            if self.batch_registry.get(pkg_id) == "COMPLETED":
                continue

            self.batch_registry[pkg_id] = "PENDING"
            await self.input_queue.put(pkg_id)

        await self.input_queue.join()

        self._is_running = False
        for task in self.phalanx_tasks:
            task.cancel()

        if self.flusher_task:
            self.flusher_task.cancel()
        if self.tuner_task:
            self.tuner_task.cancel()

        await asyncio.gather(
            *self.phalanx_tasks, self.flusher_task, self.tuner_task, return_exceptions=True
        )

    async def _worker_loop(self) -> None:
        while self._is_running:
            try:
                pkg_id = await self.input_queue.get()
                self.batch_registry[pkg_id] = "IN_PROGRESS"

                raw_payload = await self._registry_client.fetch(pkg_id)
                if not raw_payload:
                    self._error_count += 1
                    self.batch_registry[pkg_id] = "FAILED"
                    self.quarantined_nodes.add(pkg_id)
                    self.input_queue.task_done()
                    continue

                records = self._parser_kernel.flatten(raw_payload)

                for record in records:
                    await self.output_queue.put(record)

                self.batch_registry[pkg_id] = "COMPLETED"
                self._total_processed += 1
                self.input_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception:
                self._error_count += 1
                self.batch_registry[pkg_id] = "FAILED"
                self.quarantined_nodes.add(pkg_id)
                self.input_queue.task_done()

    async def _persistence_flusher(self) -> None:
        batch = []
        while self._is_running or not self.output_queue.empty():
            try:
                try:
                    record = await asyncio.wait_for(self.output_queue.get(), timeout=1.0)
                    batch.append(record)
                    self.output_queue.task_done()
                except asyncio.TimeoutError:
                    pass

                if len(batch) >= self.batch_size or (
                    batch and not self._is_running and self.output_queue.empty()
                ):
                    await self._persistence_beast.bulk_upsert(batch)
                    batch.clear()

                    if self.hardware_tier != "redline":
                        await asyncio.sleep(0.015)

            except asyncio.CancelledError:
                if batch:
                    await self._persistence_beast.bulk_upsert(batch)
                break
            except Exception:
                await asyncio.sleep(1.0)

    async def _tune_performance(self) -> None:  # noqa: C901) -> None:
        while self._is_running:
            try:
                await asyncio.sleep(5.0)

                if self.hardware_tier == "redline":
                    continue

                in_q_size = self.input_queue.qsize()
                out_q_size = self.output_queue.qsize()

                if out_q_size > self.q_size * 0.8:
                    if self.concurrency_limit > 2:
                        self.concurrency_limit -= 1
                elif in_q_size > self.q_size * 0.8 and out_q_size < self.q_size * 0.2:
                    if self.concurrency_limit < 8:
                        self.concurrency_limit += 1

                while len(self.phalanx_tasks) < self.concurrency_limit:
                    task = asyncio.create_task(self._worker_loop())
                    self.phalanx_tasks.append(task)

                while len(self.phalanx_tasks) > self.concurrency_limit:
                    task = self.phalanx_tasks.pop()
                    task.cancel()

            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1.0)
