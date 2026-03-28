"""
Resiliency configuration for asynchronous registry clients.
Manages tri-phasic timeouts, hardware-aware backpressure, and exception recovery.
"""

import asyncio
import logging
import random
from typing import AsyncGenerator, Callable, Any, Awaitable

import aiohttp

from .exceptions import RegistryTimeoutError, RegistryRateLimitError, RegistryError
from .transport import TransportKernel

logger = logging.getLogger(__name__)


class ResiliencyKernel:
    __slots__ = ("_hardware_tier", "_semaphore", "_timeout", "_max_retries", "_transport")

    def __init__(self, hardware_tier: str, transport: TransportKernel):
        self._hardware_tier = hardware_tier
        self._transport = transport
        self._max_retries = 3

        slots = 200 if hardware_tier == "REDLINE" else 15
        self._semaphore = asyncio.Semaphore(slots)

        self._timeout = aiohttp.ClientTimeout(total=30, connect=5, sock_read=10)

    @property
    def timeout(self) -> aiohttp.ClientTimeout:
        return self._timeout

    async def _apply_backoff(self, attempt: int):
        if attempt > 0:
            delay = (2**attempt) + random.uniform(0, 1)
            logger.debug(f"Applying exponential backoff: {delay:.2f} seconds")
            await asyncio.sleep(delay)

    async def _inject_micro_yield(self):
        if self._hardware_tier != "REDLINE":
            await asyncio.sleep(0.001)

    async def execute_with_resiliency(
        self, request_func: Callable[[], Awaitable[aiohttp.ClientResponse]], url: str
    ) -> aiohttp.ClientResponse:

        async with self._semaphore:
            await self._inject_micro_yield()

            for attempt in range(self._max_retries + 1):
                try:
                    await self._apply_backoff(attempt)
                    response = await request_func()

                    if response.status == 429:
                        if attempt == self._max_retries:
                            raise RegistryRateLimitError(
                                f"Rate limit exceeded after {attempt} retries: {url}"
                            )
                        continue

                    return response

                except asyncio.TimeoutError:
                    if attempt == self._max_retries:
                        raise RegistryTimeoutError(
                            f"Request timeout after {attempt} retries: {url}"
                        )
                except (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError) as e:
                    if attempt == self._max_retries:
                        raise self._transport.map_socket_exception(e, url)
                except Exception as e:
                    if attempt == self._max_retries:
                        if isinstance(e, RegistryError):
                            raise
                        raise RegistryError(f"Request failed: {str(e)} [{url}]")

    async def stream_with_resiliency(
        self, response: aiohttp.ClientResponse, chunk_size: int = 65536
    ) -> AsyncGenerator[bytes, None]:

        try:
            async for chunk in self._transport.iter_chunks(response, chunk_size):
                await self._inject_micro_yield()
                yield chunk
        except asyncio.TimeoutError:
            raise RegistryTimeoutError("Socket read timeout during chunked extraction")
        except Exception as e:
            raise RegistryError(f"Stream interrupted: {str(e)}")
