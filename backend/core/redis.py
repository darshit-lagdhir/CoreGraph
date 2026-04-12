from core.config import settings
from redis.asyncio import Redis, ConnectionPool
pool = ConnectionPool.from_url((settings.REDIS_URL.unicode_string() if hasattr(settings.REDIS_URL, 'unicode_string') else str(settings.REDIS_URL)),max_connections=64000,timeout=5.0,socket_timeout=5.0,decode_responses=False)
redis_client = Redis(connection_pool=pool)
