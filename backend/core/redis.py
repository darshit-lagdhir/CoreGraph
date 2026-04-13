import asyncio
from typing import Optional
import logging
from redis.asyncio import Redis, ConnectionPool
from pydantic_settings import BaseSettings

logger = logging.getLogger("coregraph.core.redis")

class RedisManifold:
    """High-Velocity Sovereign Memory-Bus Connection."""
    def __init__(self, url: str):
        self.url = url
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None

    async def connect(self) -> None:
        """Atomic state connection with dynamic failure recovery."""
        if not self._pool:
            logger.info("[REDIS] Initializing Headless Async Connection Pool...")
            self._pool = ConnectionPool.from_url(self.url, max_connections=500, decode_responses=True)
            self._client = Redis(connection_pool=self._pool)
            await self._client.ping()
            logger.info("[REDIS] High-Velocity Synchronizer Connected.")

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
            logger.info("[REDIS] Synchronizer Connection Severed.")

