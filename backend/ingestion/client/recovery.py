"""
Recovery kernel for asynchronous dependencies processing.
Handles transient failures, backoff algorithms, and persistence handshakes.
"""

import asyncio
import logging
import random
from typing import Callable, Awaitable, Any, Dict, Optional

import aiohttp

from .exceptions import (
    RegistryTimeoutError,
    RegistryRateLimitError,
    RegistryError,
    RegistryProtocolError,
    RegistryAddressError,
)

logger = logging.getLogger(__name__)


class RecoveryKernel:
    __slots__ = (
        "_hardware_tier",
        "_base_delay",
        "_jitter_max",
        "_max_retries",
        "_telemetry_cache",
        "_persistence_queue",
    )

    def __init__(self, hardware_tier: str = "POTATO"):
        self._hardware_tier = hardware_tier
        self._telemetry_cache: Dict[str, int] = {}
        self._persistence_queue = asyncio.Queue()

        if hardware_tier == "REDLINE":
            self._base_delay = 1.0
            self._jitter_max = 1.5
            self._max_retries = 3
        else:
            self._base_delay = 2.0
            self._jitter_max = 2.5
            self._max_retries = 3

    def _is_transient(self, exception: Exception) -> bool:
        if isinstance(exception, RegistryProtocolError):
            return False
        if isinstance(exception, aiohttp.ClientResponseError):
            if exception.status in (401, 403, 404):
                return False
        return True

    async def _apply_backoff(self, attempt: int):
        if attempt > 0:
            delay = (self._base_delay * (2**attempt)) + random.uniform(0, self._jitter_max)
            await asyncio.sleep(delay)

    def _record_telemetry(self, error_type: str, url: str):
        if error_type not in self._telemetry_cache:
            self._telemetry_cache[error_type] = 1
            logger.error(f"First occurrence - {error_type} at {url}")
        else:
            self._telemetry_cache[error_type] += 1
            if self._telemetry_cache[error_type] % 500 == 0:
                logger.warning(
                    f"Accumulated {self._telemetry_cache[error_type]} events for {error_type}"
                )

    async def _requeue_node(self, node_id: str, reason: str):
        await self._persistence_queue.put(
            {"node": node_id, "status": "PENDING_RECOVERY", "reason": reason}
        )
        logger.debug(f"Queued node {node_id} for secondary forensic extraction.")

    async def execute(
        self, request_func: Callable[[], Awaitable[aiohttp.ClientResponse]], url: str, node_id: str
    ) -> Optional[aiohttp.ClientResponse]:

        for attempt in range(self._max_retries + 1):
            try:
                await self._apply_backoff(attempt)
                response = await request_func()

                if response.status == 429:
                    if attempt == self._max_retries:
                        self._record_telemetry("RATE_LIMIT", url)
                        await self._requeue_node(node_id, "RATE_LIMIT_EXHAUSTED")
                        return None
                    continue

                if response.status in (401, 403, 404):
                    self._record_telemetry(f"HTTP_{response.status}", url)
                    await self._requeue_node(node_id, f"TERMINAL_HTTP_{response.status}")
                    return None

                response.raise_for_status()
                return response

            except Exception as e:
                error_name = e.__class__.__name__

                if not self._is_transient(e):
                    self._record_telemetry(f"TERMINAL_{error_name}", url)
                    await self._requeue_node(node_id, "TERMINAL_EXCEPTION")
                    return None

                if attempt == self._max_retries:
                    self._record_telemetry(f"EXHAUSTED_{error_name}", url)
                    await self._requeue_node(node_id, "RETRIES_EXHAUSTED")
                    return None
