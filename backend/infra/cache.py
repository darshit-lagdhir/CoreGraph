import os
import redis.asyncio as redis
import json
import struct
from typing import Dict, Any
class MetricDebouncer:
    __slots__ = ('redis_url', 'client')
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        pool = redis.ConnectionPool.from_url(self.redis_url, max_connections=64000, decode_responses=False)
        self.client = redis.Redis(connection_pool=pool)
    async def buffer_metric(self, author_id: str, package_id: str, field: str, value: int = 1):
        key = f'debounce:metrics:{author_id}:{package_id}'.encode('utf-8')
        b_field = field.encode('utf-8')
        pipe = self.client.pipeline(transaction=True)
        pipe.hincrby(key, b_field, value)
        pipe.expire(key, 7200)
        await pipe.execute()
    async def get_all_pending(self) -> Dict[str, Dict[str, str]]:
        pending: Dict[str, Dict[str, str]] = {}
        cursor = b'0'
        while True:
            cursor, keys = await self.client.scan(cursor=cursor, match=b'debounce:metrics:*', count=5000)
            for k in keys:
                raw_hash = await self.client.hgetall(k)
                if not raw_hash: continue
                pending[k.decode('utf-8')] = {fk.decode('utf-8'): fv.decode('utf-8') for fk,fv in raw_hash.items()}
            if cursor == b'0': break
        return pending
    async def clear_key(self, key: str):
        await self.client.delete(key.encode('utf-8'))
cache_debouncer = MetricDebouncer()
