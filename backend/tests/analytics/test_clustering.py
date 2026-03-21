import networkx as nx
import numpy as np
import pytest
from analytics.clustering import CommunityDetector


def generate_benchmark_cluster(node_count: int, edge_probability: float, cluster_id: int):
    # Generating a Girvan-Newman localized neighborhood
    G = nx.erdos_renyi_graph(node_count, edge_probability, seed=cluster_id)
    # Mapping to DiGraph with weighted intentionality
    DG = nx.DiGraph(G)
    for u, v in DG.edges():
        DG[u][v]["is_direct"] = True
    return DG


def test_community_determinism_seed():
    # Failure 1 Resolution: Seeded stability across worker nodes
    G1 = generate_benchmark_cluster(100, 0.1, 42)
    G2 = generate_benchmark_cluster(100, 0.1, 42)

    # Ensuring identical topology
    assert list(G1.edges()) == list(G2.edges())

    detector1 = CommunityDetector(G1, "npm")
    detector2 = CommunityDetector(G2, "npm")

    res1 = detector1.calculate()
    res2 = detector2.calculate()

    # Asserts identical cluster IDs for same ecosystem/date
    for node in res1.nodes():
        assert res1.nodes[node]["cluster_id"] == res2.nodes[node]["cluster_id"]


def test_sparse_memory_stress_threshold():
    # Failure 2 Resolution: Sparse Matrix Memory Shield (avoiding dense O(N^2))
    # We test with a medium size that would be expensive if dense
    node_count = 10000
    G = nx.DiGraph()
    for i in range(node_count):
        G.add_node(i)
        # Adding some sparse edges
        G.add_edge(i, (i + 1) % node_count, is_direct=True)
        G.add_edge(i, (i + 5) % node_count, is_direct=False)

    # Ensuring we can calculate without a MemoryError on the 8GB hypervisor
    detector = CommunityDetector(G, "go")
    res = detector.calculate()

    # Verifying topological coverage
    for node in res.nodes():
        assert "cluster_id" in res.nodes[node]


def test_modularity_threshold_assertion():
    # Asserts the algorithm successfully identifies structural non-randomness
    # Creating two disjoint clusters connected by a bridge
    G = nx.union(
        generate_benchmark_cluster(50, 0.2, 1),
        generate_benchmark_cluster(50, 0.2, 2),
        rename=("A-", "B-"),
    )
    # Add a bridge node
    G.add_edge("A-1", "B-1", is_direct=False)

    detector = CommunityDetector(G, "pypi")
    res = detector.calculate()

    # Nodes in the same cluster should share a cluster ID
    # Usually cluster A will be one CID and B will be another
    assert res.nodes["A-5"]["cluster_id"] != res.nodes["B-5"]["cluster_id"]
