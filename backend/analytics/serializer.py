import gzip
import json
import networkx as nx
from redis.asyncio import Redis
from config import settings

async def serialize_and_cache(graph: nx.DiGraph, ecosystem: str) -> str:
    payload = nx.node_link_data(graph)
    json_bytes = json.dumps(payload).encode("utf-8")
    compressed_blob = gzip.compress(json_bytes)
    
    cache_key = f"coregraph:ecosystem:{ecosystem.upper()}"
    redis_client = Redis.from_url(settings.REDIS_URL)
    
    await redis_client.setex(
        name=cache_key,
        time=43200,
        value=compressed_blob
    )
    
    await redis_client.aclose()
    return cache_key
