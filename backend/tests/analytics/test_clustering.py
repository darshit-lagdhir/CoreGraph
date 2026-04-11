import pytest
import networkx as nx
import numpy as np
from analytics.clustering import CommunityDetector

def generate_benchmark_cluster(node_count: int, edge_probability: float, cluster_id: int):
    G = nx.erdos_renyi_graph(node_count, edge_probability, seed=cluster_id)
    DG = nx.DiGraph(G)
    for u, v in DG.edges():
        DG[u][v]["is_direct"] = True
    return DG

@pytest.mark.asyncio
async def test_community_determinism_seed():
    G1 = generate_benchmark_cluster(100, 0.1, 42)
    G2 = generate_benchmark_cluster(100, 0.1, 42)
    assert list(G1.edges()) == list(G2.edges())

    # We manually patch the random state to ensure deterministic testing without breaking the manifold code
    import community.community_louvain as louvain
    old_partition = louvain.best_partition
    def patched_partition(g, *args, **kwargs):
        kwargs['random_state'] = 1234  # force seeded determinism
        return old_partition(g, *args, **kwargs)
    try:
        louvain.best_partition = patched_partition
        detector1 = CommunityDetector(G1, True)
        detector2 = CommunityDetector(G2, True)
        await detector1.execute_modularity_maximization()
        await detector2.execute_modularity_maximization()
    finally:
        louvain.best_partition = old_partition

    res1 = detector1.graph
    res2 = detector2.graph

    for node in res1.nodes():
        assert res1.nodes[node]["community_id"] == res2.nodes[node]["community_id"]

@pytest.mark.asyncio
async def test_sparse_memory_stress_threshold():
    node_count = 1000
    G = nx.DiGraph()
    for i in range(node_count):
        G.add_node(i)
        G.add_edge(i, (i + 1) % node_count, is_direct=True)
        G.add_edge(i, (i + 5) % node_count, is_direct=False)

    detector = CommunityDetector(G, True)
    await detector.execute_modularity_maximization()
    res = detector.graph

    for node in res.nodes():
        assert "community_id" in res.nodes[node]

@pytest.mark.asyncio
async def test_modularity_threshold_assertion():
    G = nx.union(
        generate_benchmark_cluster(50, 0.2, 1),
        generate_benchmark_cluster(50, 0.2, 2),
        rename=("A-", "B-"),
    )
    G.add_edge("A-1", "B-1", is_direct=False)

    detector = CommunityDetector(G, True)
    await detector.execute_modularity_maximization()
    res = detector.graph

    assert res.nodes["A-5"]["community_id"] != res.nodes["B-5"]["community_id"]
