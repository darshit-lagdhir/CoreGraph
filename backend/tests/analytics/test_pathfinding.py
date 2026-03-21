import pytest
import networkx as nx
from analytics.pathfinder import Pathfinder
from analytics.propagation import RiskPropagator


def generate_directed_dag(node_count: int, edge_density: float):
    G = nx.fast_gnp_random_graph(node_count, edge_density, directed=True)
    # Ensure DAG property
    DG = nx.DiGraph([(u, v) for (u, v) in G.edges() if u < v])
    for n in DG.nodes():
        DG.nodes[n]["pagerank"] = 0.5
        DG.nodes[n]["depth"] = n  # Simple depth heuristic
    return DG


def test_dijkstra_shortest_path_accuracy():
    # Creating redundant paths with different centrality
    # Path 1: A -> B -> C (2 steps, B is high centrality)
    # Path 2: A -> D -> C (2 steps, D is low centrality)
    G = nx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    G.add_edge("A", "D")
    G.add_edge("D", "C")

    # B is critical infra (high PR), D is obscure (low PR)
    G.nodes["A"]["pagerank"] = 0.5
    G.nodes["B"]["pagerank"] = 1.0
    G.nodes["C"]["pagerank"] = 0.5
    G.nodes["D"]["pagerank"] = 0.0

    # Costs:
    # A->B: 1 + 1/(1+1.0) = 1.5
    # B->C: 1 + 1/(1+0.5) = 1.66
    # Total A-B-C ~= 3.16

    # A->D: 1 + 1/(1+0.0) = 2.0
    # D->C: 1 + 1/(1+0.5) = 1.66
    # Total A-D-C ~= 3.66

    pathfinder = Pathfinder(G)
    path = pathfinder.dijkstra("A", "C")

    assert path == ["A", "B", "C"]


def test_a_star_admissibility_bias_drift():
    # Failure 1 Resolution: Admissibility in deep DAGs
    G = generate_directed_dag(100, 0.05)

    source = 0
    target = 99

    # Dijkstra path length
    pathfinder = Pathfinder(G)
    d_path = pathfinder.dijkstra(str(source), str(target))
    a_path = pathfinder.a_star(str(source), str(target))

    # Path lengths must be identical for an admissible heuristic
    assert len(d_path) == len(a_path)


def test_cycle_resistance_audit():
    # Intentionally introducing circular dependencies
    G = nx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    G.add_edge("C", "A")  # Circular loop
    G.add_edge("B", "D")

    for n in G.nodes():
        G.nodes[n]["pagerank"] = 0.1
        G.nodes[n]["depth"] = 0

    pathfinder = Pathfinder(G)
    path = pathfinder.dijkstra("A", "D")

    assert path == ["A", "B", "D"]


def test_propagation_decay_formula():
    G = nx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    G.nodes["A"]["cvi"] = 100.0
    G.nodes["B"]["cvi"] = 0.0
    G.nodes["C"]["cvi"] = 0.0

    propagator = RiskPropagator(G, decay_factor=0.9)
    # Invert for impact search (upward)
    impacts = propagator.calculate_transitive_impact("A")

    # At d=0, A=100. At d=1, ancestor not in graph? No, B is target of A.
    # We search predecessors (parents) of A? No, dependencies go downward.
    # Risk flows Upward.
    assert impacts["A"] == 100.0
    # Add a predecessor to test upward flow
    G.add_edge("X", "A")
    impacts = propagator.calculate_transitive_impact("A")
    assert impacts["X"] == 90.0  # d=1
