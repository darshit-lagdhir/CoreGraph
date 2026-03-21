from core.config import settings
from redis.asyncio import Redis

# Unified asynchronous message broker registry for the CoreGraph cluster
redis_client = Redis.from_url(
    (
        settings.REDIS_URL.unicode_string()
        if hasattr(settings.REDIS_URL, "unicode_string")
        else str(settings.REDIS_URL)
    ),
    decode_responses=True,
)
