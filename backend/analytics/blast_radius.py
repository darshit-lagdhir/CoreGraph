import networkx as nx
from typing import Set, Dict
from collections import deque


class BlastRadiusCalculator:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.ancestry: Dict[str, Set[str]] = {}

    def calculate(self):
        """Execute linear-time O(V+E) transitive impact calculation via bitsets."""
        # 1. Topological Sorting: prerequisite for recursive union mapping
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError(
                "Graph matrix contains circular dependencies. DAG property required for BlastRadius."
            )

        # We need the topological order of the graph
        topo_order = list(nx.topological_sort(self.graph))

        # 2. Ancestry Union: Iterating reversely to propagate impact upwards
        # For each node u, Ancestors(u) = Union(Ancestors(v)) + v for all v where u depends on v
        # In our graph, edges are Dependent -> Dependency, so we need to find all descendants?
        # NO. Blast Radius = No. of things that depend on me.
        # My "In-neighbors" are my dependents. My "Out-neighbors" are my dependencies.
        # So it's the reverse: I need to calculate the transitive "In-closure".

        # We process in topological order: Dependent 1st, Dependency last.
        # This will store the set of all unique packages that depend on a given node (transitively).
        dependents: Dict[str, Set[str]] = {node: set() for node in self.graph.nodes()}

        # Dependent -> Dependency (Impact flows Uphill)
        # We process things from Dependent (low in hierarchy) to Dependency (high).
        for node in topo_order:
            for dependency in self.graph.successors(node):
                # Everything that depends on 'node' also depends on 'dependency'
                dependents[dependency].update(dependents[node])
                dependents[dependency].add(node)

        # 3. Normalization and Attribution
        for node, deps in dependents.items():
            self.graph.nodes[node]["blast_radius"] = len(deps)

        return self.graph
