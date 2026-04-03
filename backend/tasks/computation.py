import asyncio

from analytics import (
    build_acyclic_graph,
    calculate_blast_radius,
    calculate_pagerank,
    evaluate_cvi,
    serialize_and_cache,
)
from worker import celery_app


@celery_app.task(name="compute_ecosystem_metrics")
def compute_ecosystem_metrics(ecosystem: str):
    loop = asyncio.get_event_loop()

    graph = loop.run_until_complete(build_acyclic_graph(ecosystem))
    if len(graph) == 0:
        return {"status": "error", "detail": "Empty topology"}

    graph = calculate_pagerank(graph)
    graph = calculate_blast_radius(graph)
    graph = evaluate_cvi(graph)

    cache_key = loop.run_until_complete(serialize_and_cache(graph, ecosystem))

    return {"status": "success", "cache_key": cache_key}
