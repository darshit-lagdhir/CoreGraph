import os
import redis.asyncio as redis
import logging


class GraphCacheManager:
    """
    The High-Velocity Memory Mirror. (Task 010 Architecture).
    Ensures that the 144Hz HUD pulls from Redis L3 cache, not the NVMe vault.
    """

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        self.client = redis.from_url(self.redis_url, decode_responses=True)

    async def invalidate_node(self, node_id: str):
        """Surgical purging of the cached intelligence object."""
        key = f"cache:intel:{node_id}"
        await self.client.delete(key)
        # logging.info(f"[CACHE_MANAGER] Invalidated leaf: {node_id}")

    async def get_node(self, node_id: str):
        """Retrieves the cached I_Omega blob."""
        return await self.client.get(f"cache:intel:{node_id}")


# Centralized Singleton for the DAL engine
cache_manager = GraphCacheManager()
