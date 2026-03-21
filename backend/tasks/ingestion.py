import httpx
from celery import group, chord
from worker import celery_app, CoreGraphTask
from sqlalchemy.exc import OperationalError

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
    return {"status": "COMPLETED", "ecosystem": ecosystem, "target_name": target_name, "total_chunks": len(results)}
