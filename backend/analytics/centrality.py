from typing import Any, Dict, List, Optional, Set, Callable, Union
import networkx as nx


def calculate_pagerank(graph: nx.DiGraph) -> nx.DiGraph:
    if len(graph) == 0:
        return graph

    pagerank_scores = nx.pagerank(graph, alpha=0.85)
    nx.set_node_attributes(graph, pagerank_scores, "pagerank")
    return graph
