import httpx
from celery import group, chord
from worker import celery_app, CoreGraphTask
from sqlalchemy.exc import OperationalError
from redis.asyncio import Redis
import asyncio
import json

from analytics.graph_builder import GraphBuilder
from analytics.blast_radius import BlastRadiusCalculator
from analytics.cvi_calculator import CVICalculator
from analytics.serializer import GraphSerializer
from config import settings

@celery_app.task(bind=True, base=CoreGraphTask, queue='ingestion', 
                 autoretry_for=(httpx.HTTPError, OperationalError), 
                 retry_backoff=True, max_retries=5, 
                 soft_time_limit=60, time_limit=90)
def ingest_ecosystem_structure(self, ecosystem: str, target_name: str):
    total_nodes = 5000
    cores = 16
    chunk_size = max(10, min(100, total_nodes // cores))
    node_chunks = [list(range(i, min(i + chunk_size, total_nodes))) for i in range(0, total_nodes, chunk_size)]
    
    enrichment_group = group(enrich_node_telemetry.s(ecosystem, chunk) for chunk in node_chunks)
    callback = finalize_ingestion.s(ecosystem, target_name)
    
    chord(enrichment_group)(callback)
    
    return {"status": "seed_completed", "chunks_generated": len(node_chunks)}

@celery_app.task(bind=True, base=CoreGraphTask, queue='ingestion', 
                 autoretry_for=(httpx.HTTPError, OperationalError), 
                 retry_backoff=True, max_retries=5, 
                 soft_time_limit=60, time_limit=90)
def enrich_node_telemetry(self, ecosystem: str, node_ids: list):
    return {"status": "chunk_enriched", "size": len(node_ids)}

@celery_app.task(bind=True, base=CoreGraphTask, queue='ingestion')
def finalize_ingestion(self, results, ecosystem: str, target_name: str):
    """Execute analytical fusion mapping and notify the WebSocket telemetry terminal."""
    
    async def run_analytics():
        # 1. Building the structural DAG from PostgreSQL records
        builder = GraphBuilder(ecosystem)
        graph = await builder.build()
        
        # 2. Transitive Impact: Blast Radius Calculation
        br_calc = BlastRadiusCalculator(graph)
        graph = br_calc.calculate()
        
        # 3. Structural Importance: CVI / PageRank Fusion
        cvi_calc = CVICalculator(graph)
        graph = cvi_calc.calculate()
        
        # 4. Serialization: Binary gzipped payload generated for Redis caching
        serializer = GraphSerializer(graph)
        compressed_payload = serializer.serialize()
        
        # 5. Persistence: Caching the analytical metrics in Redis (TTL 12h)
        redis_client = Redis.from_url(settings.REDIS_URL)
        cache_key = f"coregraph:pkg:{ecosystem}:{target_name}"
        await redis_client.set(cache_key, compressed_payload, ex=43200) # 12 hours
        
        # 6. Synchronization: Pub/Sub broadcast notifying the ASGI Gateway
        # This triggers the 'coregraph:telemetry' WebSocket stream in real-time
        await redis_client.publish("coregraph:telemetry", compressed_payload)
        
        await redis_client.aclose()
        return len(graph.nodes())

    # Running async builder within Celery worker thread execution bounds
    nodes_count = asyncio.run(run_analytics())
    
    return {
        "status": "ANALYTICS_SYNCHRONIZED", 
        "ecosystem": ecosystem, 
        "target_name": target_name, 
        "total_nodes": nodes_count,
        "total_chunks_processed": len(results)
    }
