import asyncio
import os
import logging
import time
import asyncpg
import json
import numpy as np
from typing import List, Dict, Any
from backend.core.sharding.hadronic_pool import uhmp_pool
from backend.core.memory_manager import metabolic_governor

logger = logging.getLogger(__name__)


class HydrationIgnitionSystem:
    """
    SECTOR BETA: Supabase Hydration Kernel (REAL DATA EXTRACTION).
    Extracts the surgical 5000-node slice from the 3.81M Hadronic Core.
    """

    def __init__(self, db_url: str = None):
        raw_url = db_url or os.getenv("CLOUD_DATABASE_URL")
        # Normalize for asyncpg (remove SQLAlchemy +asyncpg driver prefix)
        if raw_url and "+asyncpg" in raw_url:
            self.db_url = raw_url.replace("+asyncpg", "")
        else:
            self.db_url = raw_url

        self.batch_size = 500  # Sector Beta: High-density packet size
        self.max_nodes = 5000  # Sector Alpha: Surgical Slice Limit

    async def extract_high_entropy_shards(self) -> Dict[str, Any]:
        """
        Sector Alpha: Performs REAL topological analysis on the UHMP Substrate.
        Identifies nodes with the highest utility/entropy scores.
        """
        logger.info("[Alpha] Commencing REAL Surgical Slice extraction from Hadronic Core...")

        # Sector Alpha: Information Density Calculation
        # Convert memory-mapped utility view to numpy for high-speed analysis
        utility_scores = np.frombuffer(uhmp_pool.utility_view, dtype=np.float32)

        # Identify top 5000 indices (Highest Systemic Risk/Utility)
        # Using argpartition for O(N) selection of top k
        if len(utility_scores) > self.max_nodes:
            top_indices = np.argpartition(utility_scores, -self.max_nodes)[-self.max_nodes :]
            # Sort them by utility for deterministic processing
            top_indices = top_indices[np.argsort(-utility_scores[top_indices])]
        else:
            top_indices = np.arange(len(utility_scores))

        extracted_nodes = []
        extracted_edges = []

        logger.info(f"[Alpha] Analyzing {len(top_indices)} top-tier nodes...")

        for idx in top_indices:
            idx = int(idx)
            utility = float(utility_scores[idx])

            # Map index to forensic node ID
            node_id = f"node_{idx:07d}"

            # Sector Alpha: Metadata construction
            extracted_nodes.append(
                {
                    "id": node_id,
                    "risk_weight": utility,
                    "metadata": {"local_index": idx, "spectral_entropy": utility},
                    "topology_vector": [0.0, 0.0, 0.0],  # Initial spatial state
                }
            )

            # Sector Gamma: Relational Mapping (Unpacking Edge View)
            # Each node has a 128-bit slot (2x64) in the relational manifold
            packed = uhmp_pool.edge_view[idx * 2]
            if packed > 0:
                target_idx = int(packed >> 32)
                edge_type = int((packed >> 28) & 0xF)
                weight = float(packed & 0x0FFFFFFF)

                target_id = f"node_{target_idx:07d}"
                extracted_edges.append(
                    {
                        "source_id": node_id,
                        "target_id": target_id,
                        "weight": weight,
                        "type": edge_type,
                    }
                )

        # Sector Epsilon: Memory Police Oversight check
        rss = metabolic_governor.get_physical_rss_us()
        logger.info(
            f"[Alpha] Extraction Complete. Nodes: {len(extracted_nodes)}, Edges: {len(extracted_edges)}. RSS: {rss:.2f}MB"
        )

        return {"nodes": extracted_nodes, "edges": extracted_edges}

    async def ignite_hydration(self, data: Dict[str, Any]):
        """
        Sector Beta: Parallel upload of REAL forensic shards via Supabase Data Bridge.
        """
        if not self.db_url:
            logger.error("[Beta] CLOUD_DATABASE_URL missing. Ignition aborted.")
            return

        nodes = data["nodes"]
        edges = data["edges"]

        logger.info(f"[Beta] Igniting hydration for {len(nodes)} nodes and {len(edges)} edges.")

        try:
            conn = await asyncpg.connect(self.db_url)

            # Sector Gamma: Dual-Pass Strategy (Nodes then Edges)

            # Pass 1: Seed Nodes
            logger.info("[Beta] Pass 1: Seeding high-entropy nodes...")
            for i in range(0, len(nodes), self.batch_size):
                batch = nodes[i : i + self.batch_size]
                # Format for fast batch insert
                records = [
                    (n["id"], n["risk_weight"], json.dumps(n["metadata"]), n["topology_vector"])
                    for n in batch
                ]
                await conn.copy_records_to_table(
                    "nodes",
                    records=records,
                    columns=["id", "risk_weight", "metadata", "topology_vector"],
                )
                logger.info(f"[Beta] Committed node batch {i//self.batch_size + 1}")

            # Pass 2: Inject Adjacency Matrix Shards
            logger.info("[Beta] Pass 2: Injecting topological edges...")
            # We filter edges to ensure target nodes exist in our 5000-node shard or handle dangles
            # For the demo, we only upload edges where both nodes are in the surgical slice
            node_ids = {n["id"] for n in nodes}
            valid_edges = [e for e in edges if e["target_id"] in node_ids]

            for i in range(0, len(valid_edges), self.batch_size):
                batch = valid_edges[i : i + self.batch_size]
                records = [(e["source_id"], e["target_id"], e["weight"]) for e in batch]
                await conn.copy_records_to_table(
                    "edges", records=records, columns=["source_id", "target_id", "weight"]
                )
                logger.info(f"[Beta] Committed edge batch {i//self.batch_size + 1}")

            await conn.close()
            logger.info("[Beta] Hydration Genesis Complete. REAL Data Manifested.")
        except Exception as e:
            logger.error(f"[Beta] Hydration failed: {e}")


if __name__ == "__main__":

    async def test_real_hydration():
        print("--- [TEST] REAL HydrationIgnitionSystem Genesis ---")
        kernel = HydrationIgnitionSystem()

        data = await kernel.extract_high_entropy_shards()
        print(f"Extracted {len(data['nodes'])} REAL nodes and {len(data['edges'])} REAL edges.")

        # Test ignition only if URL exists and is valid
        if kernel.db_url and "supabase.co" in kernel.db_url:
            print("Igniting REAL Hydration to Supabase...")
            await kernel.ignite_hydration(data)
        else:
            print("Skipping ignition: Valid CLOUD_DATABASE_URL not found.")

    asyncio.run(test_real_hydration())
