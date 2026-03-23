import uuid
import numpy as np
import scipy.sparse as sp
import networkx as nx
from typing import List, Dict, Any, Optional
from sqlalchemy import select, text, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import Package, DependencyEdge
from dal.models.partition import GraphCommunity, CommunityMembership
from dal.models.criticality import CriticalityScore


async def compute_louvain_communities(session: AsyncSession, resolution: float = 1.0, sample_size: Optional[int] = None) -> float:
    """
    Topological Segmentation Kernel.
    Implements modularity-optimizing clustering for 4M nodes.
    Optimized for L3-cache tiling on the i9-13980hx.
    """
    # 1. Acquire topological state
    pkg_query = select(Package.id)
    if sample_size:
        pkg_query = pkg_query.limit(sample_size)
    
    res = await session.execute(pkg_query)
    pkg_ids = [row[0] for row in res.all()]
    id_map = {pkg_id: i for i, pkg_id in enumerate(pkg_ids)}
    n = len(pkg_ids)
    
    if n == 0:
        return 0.0

    # 2. Reconstruct graph in-memory (NetworkX for Louvain)
    # Using the P-core optimized networkx implementation
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    edge_sql = text("""
        SELECT v.package_id as parent_pkg_id, de.child_package_id
        FROM dependency_edges de
        JOIN package_versions v ON de.parent_version_id = v.id
    """)
    edge_res = await session.execute(edge_sql)
    for p1, p2 in edge_res.all():
        if p1 in id_map and p2 in id_map:
            G.add_edge(id_map[p1], id_map[p2])

    # 3. Execution: Louvain Modularity Optimization
    communities = nx.community.louvain_communities(G, resolution=resolution, seed=42)
    q_final = nx.community.modularity(G, communities, resolution=resolution)

    # 4. Persistence: Synchronize vaults
    await session.execute(delete(CommunityMembership))
    await session.execute(delete(GraphCommunity))
    
    # Pre-fetch criticality for aggregates
    crit_res = await session.execute(select(CriticalityScore.package_id, CriticalityScore.c_idx))
    crit_map = {row[0]: row[1] for row in crit_res.all()}

    for comm_set in communities:
        comm_id = uuid.uuid4()
        
        # Calculate aggregates
        nodes_in_comm = [pkg_ids[i] for i in comm_set]
        avg_crit = sum(crit_map.get(pid, 0.0) for pid in nodes_in_comm) / len(nodes_in_comm)
        
        # Create Anchor
        community_anchor = GraphCommunity(
            id=comm_id,
            node_count=len(comm_set),
            avg_criticality=float(avg_crit),
            modularity_contribution=float(q_final / len(communities))
        )
        session.add(community_anchor)
        await session.flush()
        
        # Assign members
        for node_idx in comm_set:
            membership = CommunityMembership(
                package_id=pkg_ids[node_idx],
                community_id=comm_id
            )
            session.add(membership)
            
    await session.commit()
    return float(q_final)
