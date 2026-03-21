import asyncio
import gzip
import json
import networkx as nx
from redis.asyncio import Redis

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from analytics.cvi_calculator import CVICalculator
from analytics.serializer import GraphSerializer

async def verify_synchronization_logic():
    print("Initiating Analytical Synchronization Round-Trip Integrity Audit...")

    # 1. Create Mock Analytical State
    G = nx.DiGraph()
    G.add_node("node1", name="package-a", blast_radius=10)
    G.add_node("node2", name="package-b", blast_radius=5)
    G.add_edge("node1", "node2") # node1 depends on node2

    # 2. Run Calc and Serialization
    cvi_calc = CVICalculator(G)
    G = cvi_calc.calculate()

    serializer = GraphSerializer(G)
    binary_payload = serializer.serialize()

    # 3. Simulate Gateway/Frontend Retrieval
    decompressed = gzip.decompress(binary_payload)
    parsed = json.loads(decompressed.decode('utf-8'))

    # 4. Assert Coherence
    source_node = G.nodes["node1"]
    sync_node = next(n for n in parsed["nodes"] if n["id"] == "node1")

    diff = abs(source_node["pagerank"] - sync_node["pagerank"])
    if diff < 1e-7:
        print(f"SUCCESS: Analytical convergence verified (Δ={diff:.2e})")
    else:
        print(f"FAILURE: Mathematical drift detected (Δ={diff:.2e})")
        sys.exit(1)

    print("End-to-End Synchronization Matrix Validated.")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(verify_synchronization_logic())
