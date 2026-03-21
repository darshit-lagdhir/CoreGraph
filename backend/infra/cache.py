import os
import redis.asyncio as redis
import json
from typing import Dict, Any


class MetricDebouncer:
    """
    The Behavioral Buffer.
    Prevents NVMe SSD wear and database lock contention by buffering
    high-frequency maintainer activity in the Redis cache.
    """

    def __init__(self):
        # We fetch the URL from environment/settings architecture.
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.redis_url, decode_responses=True)

    async def buffer_metric(self, author_id: str, package_id: str, field: str, value: int = 1):
        """
        High-speed in-memory increment.
        This is called by the Module 1 Crawler for every commit event identified.
        """
        key = f"debounce:metrics:{author_id}:{package_id}"
        # Atomic increment in Redis (Thread-safe by design)
        # Prevents 'Write-Storm' on the primary PostgreSQL vault.
        await self.client.hincrby(key, field, value)
        # Set a 2-hour TTL to ensure we don't leak memory in circular activity.
        await self.client.expire(key, 7200)

    async def get_all_pending(self) -> Dict[str, Dict[str, str]]:
        """Fetches all metrics that are waiting for the 'Pulse' sweep into Postgres."""
        keys = await self.client.keys("debounce:metrics:*")
        pending = {}
        for key in keys:
            # We fetch as mapping due to HINCRBY structure
            pending[key] = await self.client.hgetall(key)
        return pending

    async def clear_key(self, key: str):
        """Removes the key after successful DB persistence."""
        await self.client.delete(key)


# Centralized accessor for the debouncer
cache_debouncer = MetricDebouncer()
