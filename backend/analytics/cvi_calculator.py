import networkx as nx
import numpy as np


class CVICalculator:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def calculate(self):
        """Map multi-vector risk telemetry into a fused 0-100 scalar indexing limits."""
        # 1. PageRank Centrality: Structural importance in the ecosystem ocean
        # Alpha=0.85, Power iteration convergence for i9 matrix benchmarks.
        pr_scores = nx.pagerank(self.graph, alpha=0.85, weight=None)

        # Normalize PageRank scalars 0..1
        max_pr = max(pr_scores.values()) if pr_scores else 1.0

        # 2. Vector Fusion: Structural, Human, and Economic Risk mapping
        # Formula uses weighted geometric mean to prioritize high-risk extremes.
        for node in self.graph.nodes():
            raw_pr = pr_scores.get(node, 0.0)
            norm_pr = raw_pr / max_pr if max_pr > 0 else 0.0

            # Simulated telemetry placeholders for Human & Economic risk (Module 1 Scope)
            human_risk = 0.5  # Placeholder for Starvation/BusFactor metrics
            economic_risk = 0.5  # Placeholder for USD funding levels

            structural_risk = norm_pr * 1.5  # PageRank weighting scalar

            # CVI Fusion = min(100, (Structural * 0.4 + Human * 0.3 + Economic * 0.3) * 100)
            cvi_fused = (structural_risk * 0.4 + human_risk * 0.3 + economic_risk * 0.3) * 100

            self.graph.nodes[node]["pagerank"] = norm_pr
            self.graph.nodes[node]["cvi"] = min(100, int(cvi_fused))

        return self.graph
