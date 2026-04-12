import os
import redis.asyncio as redis
import struct
class GraphCacheManager:
    __slots__ = ('redis_url', 'client')
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
        pool = redis.ConnectionPool.from_url(self.redis_url, max_connections=64000, decode_responses=False)
        self.client = redis.Redis(connection_pool=pool)
    async def invalidate_node(self, node_id: str):
        await self.client.delete(f'cache:intel:{node_id}'.encode('utf-8'))
    async def get_node(self, node_id: str) -> bytes:
        return await self.client.get(f'cache:intel:{node_id}'.encode('utf-8'))
cache_manager = GraphCacheManager()
