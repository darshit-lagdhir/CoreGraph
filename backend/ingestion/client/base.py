"""
Base registry client for asynchronous dependency ingestion.
Orchestrates session lifecycles, concurrency limits, and memory limits.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, AsyncGenerator

import aiohttp
import ujson

from .exceptions import (
    RegistryError,
    RegistryAddressError,
    RegistrySocketResetError,
    RegistryHostDisconnectError,
    RegistryTransportError,
    RegistryTimeoutError,
    RegistryProtocolError,
    RegistryRateLimitError,
)
from .transport import TransportKernel

logger = logging.getLogger(__name__)


class BaseRegistryClient(ABC):
    """
    Abstract client for dependency ingestion.
    Manages session reuse, connection pooling, and request timeouts.
    """

    __slots__ = (
        "_session",
        "_semaphore",
        "_base_url",
        "_hardware_tier",
        "_timeout",
        "_user_agent",
        "_transport",
    )

    def __init__(self, base_url: str, hardware_tier: str = "POTATO"):
        self._base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None
        self._hardware_tier = hardware_tier
        self._user_agent = "CoreGraph/1.0"
        self._transport = TransportKernel(hardware_tier)

        slots = 200 if hardware_tier == "REDLINE" else 15
        self._semaphore = asyncio.Semaphore(slots)

        self._timeout = aiohttp.ClientTimeout(total=30, connect=5, sock_read=10)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                connector=self._transport.connector,
                timeout=self._timeout,
                headers={"User-Agent": self._user_agent},
            )
        return self._session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._session and not self._session.closed:
                await self._session.close()
                await asyncio.sleep(0.250)
        finally:
            await self._transport.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        session = await self._get_session()
        url = f"{self._base_url}/{endpoint.lstrip('/')}"

        async with self._semaphore:
            try:
                response = await session.request(method, url, **kwargs)
                if response.status == 429:
                    raise RegistryRateLimitError(f"Rate limit exceeded: {url}")
                return response
            except asyncio.TimeoutError:
                raise RegistryTimeoutError(f"Request timeout: {url}")
            except (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError) as e:
                raise self._transport.map_socket_exception(e, url)
            except Exception as e:
                if isinstance(e, RegistryError):
                    raise
                raise RegistryError(f"Request failed: {str(e)} [{url}]")

    async def fetch_json(self, endpoint: str, limit_mb: int = 50) -> Dict[str, Any]:
        response = await self._request("GET", endpoint)
        async with response:
            size = response.content_length
            if size and size > (limit_mb * 1024 * 1024):
                raise RegistryProtocolError(f"Payload exceeds {limit_mb}MB limit")
            try:
                raw_payload = await response.read()
                return ujson.loads(raw_payload)
            except (ValueError, TypeError):
                raise RegistryProtocolError(f"Invalid JSON payload at {endpoint}")

    async def stream_raw(
        self, endpoint: str, chunk_size: int = 65536
    ) -> AsyncGenerator[bytes, None]:
        response = await self._request("GET", endpoint)
        async with response:
            async for chunk in self._transport.iter_chunks(response, chunk_size):
                yield chunk
