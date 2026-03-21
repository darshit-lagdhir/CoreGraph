import asyncio
from worker import celery_app
from analytics.graph_builder import build_acyclic_graph
from analytics.centrality import calculate_pagerank
from analytics.blast_radius import calculate_blast_radius
from analytics.cvi_calculator import evaluate_cvi
from analytics.serializer import serialize_and_cache


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
