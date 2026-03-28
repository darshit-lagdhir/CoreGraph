"""
Transport layer configuration for asynchronous registry clients.
Manages connection pooling, SSL/TLS contexts, and DNS caching.
"""

import asyncio
import socket
import ssl
import logging
from typing import Optional, Dict

import aiohttp
import certifi

from .exceptions import (
    RegistryAddressError,
    RegistrySocketResetError,
    RegistryHostDisconnectError,
    RegistryTransportError,
    RegistryTimeoutError,
    RegistryProtocolError,
    RegistryError,
)

logger = logging.getLogger(__name__)


class TransportKernel:
    __slots__ = (
        "_connector",
        "_hardware_tier",
        "_limits",
        "_ssl_context",
        "_monitor_task",
        "_saturation_level",
    )

    def __init__(self, hardware_tier: str = "POTATO"):
        self._hardware_tier = hardware_tier
        self._saturation_level = 0.0
        self._limits = self._calculate_limits(hardware_tier)

        self._ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._ssl_context.set_ciphers("ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256")

        resolver = aiohttp.AsyncResolver()

        self._connector = aiohttp.TCPConnector(
            limit=self._limits["total"],
            limit_per_host=self._limits["per_host"],
            ssl=self._ssl_context,
            resolver=resolver,
            ttl_dns_cache=300,
            use_dns_cache=True,
            force_close=False,
            enable_cleanup_closed=True,
            keepalive_timeout=self._limits["keepalive"],
        )

        self._monitor_task = asyncio.create_task(self._saturation_monitor())

    def _calculate_limits(self, tier: str) -> Dict[str, int]:
        if tier == "REDLINE":
            return {"total": 500, "per_host": 50, "keepalive": 45}
        return {"total": 25, "per_host": 5, "keepalive": 30}

    async def _saturation_monitor(self):
        while self._connector and not self._connector.closed:
            try:
                active = len(self._connector._conns) if hasattr(self._connector, "_conns") else 0
                self._saturation_level = active / self._limits["total"]

                if self._saturation_level > 0.90:
                    logger.warning(f"Connection pool near capacity: {self._saturation_level:.2%}")

                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception:
                break

    @property
    def connector(self) -> aiohttp.TCPConnector:
        return self._connector

    def map_socket_exception(self, exc: Exception, url: str) -> RegistryError:
        if isinstance(exc, socket.gaierror):
            return RegistryAddressError(f"DNS resolution failed: {url}")
        if isinstance(exc, (ConnectionResetError, ConnectionAbortedError)):
            return RegistrySocketResetError(f"Connection reset by peer: {url}")
        if isinstance(exc, aiohttp.ServerDisconnectedError):
            return RegistryHostDisconnectError(f"Server disconnected: {url}")
        if isinstance(exc, aiohttp.ClientConnectorError):
            return RegistryTransportError(f"Transport connection failed: {url}")
        if isinstance(exc, asyncio.TimeoutError):
            return RegistryTimeoutError(f"Request timeout: {url}")
        return RegistryError(f"Network error: {str(exc)} [{url}]")

    async def iter_chunks(self, response: aiohttp.ClientResponse, chunk_size: int = 65536):
        async for chunk in response.content.iter_chunked(chunk_size):
            yield chunk

    async def close(self):
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        if self._connector:
            await self._connector.close()
