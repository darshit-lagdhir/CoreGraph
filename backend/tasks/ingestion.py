import httpx
from celery import group, chord
from worker import celery_app, CoreGraphTask
from sqlalchemy.exc import OperationalError
from redis.asyncio import Redis
import asyncio
import json
from typing import List, Optional, Dict, Any

from analytics.graph_builder import GraphBuilder
from analytics.blast_radius import BlastRadiusCalculator
from analytics.cvi_calculator import CVICalculator
from analytics.clustering import CommunityDetector
from analytics.serializer import GraphSerializer
from core.config import settings
from clients.ecosystems import EcosystemFactory


@celery_app.task(
    bind=True,
    base=CoreGraphTask,
    queue="ingestion",
    autoretry_for=(httpx.HTTPError, OperationalError),
    retry_backoff=True,
    max_retries=5,
    soft_time_limit=120,
    time_limit=180,
)
def ingest_ecosystem_structure(
    self: Any,
    ecosystem: str,
    target_name: str,
    depth: int = 0,
    visit_path: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Recursively ingests software topologies with depth-aware cycle breaking."""
    if visit_path is None:
        visit_path = []

    if target_name in visit_path:
        # Failure 3 Resolution: Detecting and neutralizing circular dependencies
        return {"status": "CYCLE_NEUTRALIZED", "package": target_name, "depth": depth}

    if depth > 10:  # i9 performance ceiling and 8GB RAM safety limit
        return {"status": "MAX_DEPTH_REACHED", "package": target_name}

    async def fetch_and_seed() -> int:
        async with httpx.AsyncClient() as client:
            parser = EcosystemFactory.get_client(ecosystem, client)
            try:
                metadata = await parser.fetch_metadata(target_name)
                dependencies = parser.resolve_dependencies(metadata)

                # Seed children with incremented depth and extended visit path
                new_path = visit_path + [target_name]
                child_tasks = [
                    ingest_ecosystem_structure.s(ecosystem, dep.name, depth + 1, new_path)
                    for dep in dependencies
                ]

                if child_tasks:
                    group(child_tasks).apply_async()

                return len(dependencies)
            except Exception as e:
                print(f"[INGEST_FAULT] Failed to parse {target_name}: {e}")
                return 0

    dep_count = asyncio.run(fetch_and_seed())
    return {
        "status": "INGESTION_COMPLETED",
        "package": target_name,
        "dependencies_mapped": dep_count,
    }


@celery_app.task(
    bind=True,
    base=CoreGraphTask,
    queue="ingestion",
    autoretry_for=(httpx.HTTPError, OperationalError),
    retry_backoff=True,
    max_retries=5,
    soft_time_limit=60,
    time_limit=90,
)
def enrich_node_telemetry(self: Any, ecosystem: str, node_ids: List[str]) -> Dict[str, Any]:
    return {"status": "chunk_enriched", "size": len(node_ids)}


@celery_app.task(bind=True, base=CoreGraphTask, queue="ingestion")
def finalize_ingestion(
    self: Any, results: List[Any], ecosystem: str, target_name: str
) -> Dict[str, Any]:
    """Execute analytical fusion mapping and notify the WebSocket telemetry terminal."""

    async def run_analytics() -> int:
        # 1. Building the structural DAG from PostgreSQL records
        builder = GraphBuilder(ecosystem)
        graph = await builder.build()

        # 2. Transitive Impact: Blast Radius Calculation
        br_calc = BlastRadiusCalculator(graph)
        graph = br_calc.calculate()

        # 3. Structural Importance: CVI / PageRank Fusion
        cvi_calc = CVICalculator(graph)
        graph = cvi_calc.calculate()

        # 4. Topological Segmentation: Community Detection (Louvain/Leiden)
        cluster_engine = CommunityDetector(graph, ecosystem)
        graph = cluster_engine.calculate()

        # 5. Serialization: Binary gzipped payload generated for Redis caching
        serializer = GraphSerializer(graph)
        compressed_payload = serializer.serialize()

        # 5. Persistence: Caching the analytical metrics in Redis (TTL 12h)
        redis_client = Redis.from_url(settings.REDIS_URL)
        cache_key = f"coregraph:pkg:{ecosystem}:{target_name}"
        await redis_client.set(cache_key, compressed_payload, ex=43200)  # 12 hours

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
        "total_chunks_processed": len(results),
    }
