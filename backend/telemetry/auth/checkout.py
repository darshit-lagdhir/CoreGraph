import asyncio
import time
import logging
import random
import heapq
from typing import Dict, Any, Optional

from backend.telemetry.auth.pool import TelemetryTokenPool, TokenRecord
from backend.telemetry.auth.interceptor import QuotaHeaderInterceptor


class AcquisitionRequest:
    """
    Slotted DTO tracking the priority, starvation age, and callback
    resolution events of a waiting worker. Operates as a Heap Node.
    """

    __slots__ = ("_base_priority", "_wait_start_time", "_aging_coefficient", "resolution_event")

    def __init__(self, priority: float, aging_coefficient: float):
        # Python heapq is min-heap. We invert priority float (highest absolute value = most negative)
        self._base_priority = -abs(priority)
        self._wait_start_time = time.time()
        self._aging_coefficient = aging_coefficient
        self.resolution_event = asyncio.Event()

    def get_effective_priority(self) -> float:
        """Starvation Shield Logic."""
        wait_duration = time.time() - self._wait_start_time
        aging_bonus = wait_duration * self._aging_coefficient
        # As it waits, the negative priority becomes more negative (moving it up the min-heap)
        return self._base_priority - aging_bonus

    def __lt__(self, other: "AcquisitionRequest") -> bool:
        return self.get_effective_priority() < other.get_effective_priority()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AcquisitionRequest):
            return NotImplemented
        return self.get_effective_priority() == other.get_effective_priority()


class ActiveLease:
    """Slotted tracking for the Lease Watchdog Circuit Breaker."""

    __slots__ = ("token", "checkout_time")

    def __init__(self, token: TokenRecord):
        self.token = token
        self.checkout_time = time.time()


class TokenCheckoutEngine:
    """
    Module 5 - Task 008: Token Checkout Engine and Semaphore Manifold.
    Provides hardware-aligned bounded concurrency prioritizing max-risk telemetry targets
    while preventing starvation via Dynamic Priority Aging.
    """

    __slots__ = (
        "_token_pool",
        "_interceptor",
        "_hardware_tier",
        "_semaphore",
        "_priority_queue",
        "_queue_lock",
        "_active_leases",
        "_max_lease_duration",
        "_aging_coefficient",
    )

    def __init__(
        self,
        token_pool: TelemetryTokenPool,
        interceptor: QuotaHeaderInterceptor,
        hardware_tier: str = "redline",
    ):
        self._token_pool = token_pool
        self._interceptor = interceptor
        self._hardware_tier = hardware_tier

        # Lease Watchdog Settings
        self._max_lease_duration = 30.0  # Seconds before worker abandonment assumed
        self._active_leases: Dict[str, ActiveLease] = {}

        # Hardware-Aware Concurrency Gate Limits
        if self._hardware_tier == "redline":
            # Simulating a 24-core setup * 2.5 network hiding factor
            capacity = 60
            self._aging_coefficient = 0.5
        else:
            capacity = 2
            self._aging_coefficient = 1.5  # Faster aging due to tighter pipe

        self._semaphore = asyncio.Semaphore(capacity)

        # Priority Starvation Shield Components
        self._priority_queue: list = []
        self._queue_lock = asyncio.Lock()

        # Spin up Lease Watchdog Daemon
        asyncio.create_task(self._lease_watchdog_daemon())

    async def acquire_token(
        self, forensic_priority: float = 1.0, timeout: float = 15.0
    ) -> TokenRecord:
        """
        Primary Acquisition Gate.
        Coordinates Priority-Heap insertion, Semaphore execution slots, and non-blocking timeout parameters.
        """
        request_node = AcquisitionRequest(forensic_priority, self._aging_coefficient)

        # Lock required purely for python heapq structural mutations
        async with self._queue_lock:
            heapq.heappush(self._priority_queue, request_node)

        # Thundering Herd Jitter & Resource Dispatch
        this_request_handled = False

        try:
            await asyncio.wait_for(self._dispatch_manager(), timeout=timeout)
            await request_node.resolution_event.wait()
            this_request_handled = True

            # Checkout Kernel: At this point, the worker has passed the priority gate and semaphore.
            token = await self._token_pool.acquire_token()
            self._active_leases[token.identifier] = ActiveLease(token)
            return token

        except asyncio.TimeoutError:
            if not this_request_handled:
                # Manually yank from queue to protect limits
                async with self._queue_lock:
                    try:
                        self._priority_queue.remove(request_node)
                        heapq.heapify(self._priority_queue)
                    except ValueError:
                        pass
                logging.warning(
                    f"Acquisition Anomaly: Token starvation timeout for priority P_{forensic_priority}"
                )
                raise TimeoutError("Token acquisition aborted due to system pressure.")
            else:
                # It acquired the token exactly at the timeout boundary. Fail forward.
                raise

    async def _dispatch_manager(self) -> None:
        """Internal daemon processing the top of the heap against Semaphore bound availability."""
        # Await an open execution slot
        await self._semaphore.acquire()

        async with self._queue_lock:
            if self._priority_queue:
                top_request: AcquisitionRequest = heapq.heappop(self._priority_queue)
                # Signal the specific suspended Coroutine to wake and proceed
                top_request.resolution_event.set()

    async def release_token(
        self, token_identifier: str, response_headers: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handles explicit token returns from workers.
        Clears Lease watchdog logic, triggers quota synchronization, and unlocks a new semaphore cycle.
        """
        lease_record = self._active_leases.pop(token_identifier, None)

        if lease_record and response_headers:
            # Atomic Dirty to IDLE status resolution via sensory kernel
            await self._interceptor.synchronize_token_state(token_identifier, response_headers)

        # Release the slot back to the wait line
        if lease_record:
            self._semaphore.release()
        else:
            logging.warning(
                f"Release Anomaly: Attempted release of unbound token {token_identifier}"
            )

    async def _lease_watchdog_daemon(self) -> None:
        """
        Background autonomous process hunting abandoned Leases.
        Forces the token state back to safety limits to prevent irreversible global pool drain.
        """
        while True:
            await asyncio.sleep(5.0)  # Periodic sweep

            now = time.time()
            expired_ids = []

            for t_id, lease in self._active_leases.items():
                if (now - lease.checkout_time) > self._max_lease_duration:
                    expired_ids.append(t_id)

            for e_id in expired_ids:
                logging.error(f"Lease Timeout Watchdog: Force-reclaiming abandoned token {e_id}")
                # Forcefully scrub lease and release the execution slot
                del self._active_leases[e_id]
                self._semaphore.release()
                # We do not have headers, but we release it back to the pool assuming quota is unchanged.
                # The TokenPool continues to view it as having its last registered points.
