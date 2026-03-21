import networkx as nx

def calculate_blast_radius(graph: nx.DiGraph) -> nx.DiGraph:
    try:
        ordered_nodes = list(nx.topological_sort(graph))
    except nx.NetworkXUnfeasible:
        return graph

    ordered_nodes.reverse()
    
    radius_map = {n: set() for n in graph.nodes()}
    
    for node in ordered_nodes:
        parents = list(graph.predecessors(node))
        for p in parents:
            radius_map[p].update(radius_map[node])
            radius_map[p].add(node)
            
    for node, impacted_set in radius_map.items():
        graph.nodes[node]['blast_radius'] = len(impacted_set)
        
    return graph
