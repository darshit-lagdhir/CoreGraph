import datetime
import math
import networkx as nx

def evaluate_cvi(graph: nx.DiGraph) -> nx.DiGraph:
    cvi_scores = {}
    
    for node, data in graph.nodes(data=True):
        if data.get("is_commercially_backed", False):
            deficit_score = 0.0
        else:
            budget = data.get("budget", 0.0)
            target_budget = 100000.0
            deficit_score = max(0.0, 100.0 - (budget / target_budget * 100.0))
            
        maintainers = data.get("maintainers", 0)
        burnout = 100.0
        if maintainers == 2:
            burnout = 75.0
        elif maintainers >= 5:
            burnout = 10.0
            
        last_commit = data.get("last_commit")
        if last_commit:
            try:
                dt_obj = datetime.datetime.fromisoformat(last_commit)
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=datetime.timezone.utc)
                delta = datetime.datetime.now(datetime.timezone.utc) - dt_obj
                if delta.days > 365:
                    burnout = min(100.0, burnout * 1.5)
            except (ValueError, TypeError):
                pass
                
        cvi_raw = (0.5 * deficit_score) + (0.5 * burnout)
        pagerank_scalar = data.get("pagerank", 0.0)
        cvi_final = min(100.0, cvi_raw * (1.0 + math.log10(1.0 + pagerank_scalar * 1000.0)))
        
        cvi_scores[node] = round(cvi_final, 2)
        
    nx.set_node_attributes(graph, cvi_scores, "cvi")
    return graph
