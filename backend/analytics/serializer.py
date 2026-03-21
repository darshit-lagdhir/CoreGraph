import json
import gzip
import networkx as nx
from typing import Dict, Any

class GraphSerializer:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def serialize(self) -> bytes:
        """Flatten in-memory graph structures into 64KB-friendly binary buffers."""
        # 1. Structural Flattening: Nodes and Links mapping
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "name": data.get("name", ""),
                "cvi": data.get("cvi", 0),
                "pagerank": data.get("pagerank", 0.0),
                "blast_radius": data.get("blast_radius", 0),
                "budget_usd": data.get("budget_usd", 0.0),
                "is_commercially_backed": data.get("is_commercially_backed", False)
            })

        links = []
        for source, target in self.graph.edges():
            links.append({
                "source": source,
                "target": target
            })

        payload = {
            "nodes": nodes,
            "links": links
        }

        # 2. Binary Compression: Zeroing network overhead for 50MB telemetry clusters
        # Level 9 compression for absolute hypervisor memory economy.
        raw_json = json.dumps(payload).encode('utf-8')
        compressed = gzip.compress(raw_json, compresslevel=9)
        
        return compressed

    def get_raw_size(self) -> int:
        return len(json.dumps({
            "nodes": [n for n in self.graph.nodes()],
            "links": [l for l in self.graph.edges()]
        }))
