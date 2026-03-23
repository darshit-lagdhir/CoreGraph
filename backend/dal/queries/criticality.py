import numpy as np
import scipy.sparse as sp
import uuid
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, text, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import Package, DependencyEdge
from dal.models.maintainer import MaintainerMetrics
from dal.models.criticality import CriticalityScore
from dal.queries.pathfinder import walk_upstream, calculate_blast_radius_score


async def compute_global_criticality(
    session: AsyncSession, damping: float = 0.85, max_iter: int = 50, tol: float = 1e-6
):
    """
    The Criticality Kernel (Task 013).
    Performs Power Iteration and HITS logic across the 3.88M node OSINT ocean.
    Optimized for the i9-13980hx Vectorization Engine.
    """
    # 1. Fetch all packages and map IDs to matrix indices
    res = await session.execute(select(Package.id))
    pkg_ids = [row[0] for row in res.all()]
    id_map = {pkg_id: i for i, pkg_id in enumerate(pkg_ids)}
    n = len(pkg_ids)

    if n == 0:
        return

    # 2. Build Adjacency Matrix (CSR)
    # Target (Child) -> Source (Parent/Dependent)
    # In dependency graphs, edges usually point from Parent to Child?
    # Or in our DB, 'dependency_edges' connects 'parent_version' to 'child_package'.
    # This means Parent -> Child.
    # Centrality (Importance) should flow from dependents to dependencies.
    # So we want edges from Dependents (Parents) to Dependencies (Children).

    # We'll use child_package_id as the 'target' and parent_version package_id as 'source'.
    # Wait! DependencyEdge has parent_version_id. We need the package_id of that version.
    edge_sql = text("""
        SELECT v.package_id as parent_pkg_id, de.child_package_id
        FROM dependency_edges de
        JOIN package_versions v ON de.parent_version_id = v.id
    """)
    edge_res = await session.execute(edge_sql)
    edges = edge_res.all()

    sources = []
    targets = []
    for parent_pkg_id, child_pkg_id in edges:
        if parent_pkg_id in id_map and child_pkg_id in id_map:
            sources.append(id_map[parent_pkg_id])
            targets.append(id_map[child_pkg_id])

    # Adjacency matrix A where A[i, j] = 1 if j depends on i (j -> i flow of importance)
    # Actually, if j depends on i, j's importance contributes to i's.
    # So edge is j -> i.
    adj = sp.coo_matrix((np.ones(len(sources)), (targets, sources)), shape=(n, n)).tocsr()

    # --- A. Eigenvector Centrality (Power Iteration) ---
    # b_k+1 = A * b_k / ||A * b_k||
    v = np.ones(n) / n
    for i in range(max_iter):
        v_next = adj.dot(v)
        v_next_norm = np.linalg.norm(v_next)
        if v_next_norm > 0:
            v_next = v_next / v_next_norm

        # Check convergence
        if np.linalg.norm(v_next - v) < tol:
            v = v_next
            break
        v = v_next

    # --- B. HITS Algorithm (Hubs and Authorities) ---
    # a = A * h, h = A.T * a
    authorities = np.ones(n)
    hubs = np.ones(n)
    adj_t = adj.transpose().tocsr()

    for i in range(max_iter):
        a_next = adj.dot(hubs)
        h_next = adj_t.dot(a_next)

        # Normalize
        a_norm = np.linalg.norm(a_next)
        h_norm = np.linalg.norm(h_next)
        if a_norm > 0:
            a_next /= a_norm
        if h_norm > 0:
            h_next /= h_norm

        if np.linalg.norm(a_next - authorities) < tol:
            authorities = a_next
            hubs = h_next
            break
        authorities = a_next
        hubs = h_next

    # --- C. Velocity and Blast Radius Integration ($C_{idx}$) ---
    # We'll batch fetch velocity from maintainer_metrics
    vel_res = await session.execute(
        select(MaintainerMetrics.package_id, func.max(MaintainerMetrics.current_velocity)).group_by(
            MaintainerMetrics.package_id
        )
    )
    vel_map = {row[0]: row[1] for row in vel_res.all()}

    # 4. Final Quantization and Storage
    # Formula: C_idx = 0.5 * Psi(v) + 0.2 * Vc(v) + 0.3 * ln(1 + Br(v))
    # We'll normalize centrality and authority to [0..1] range for weighting
    max_v = np.max(v) if np.max(v) > 0 else 1.0
    max_auth = np.max(authorities) if np.max(authorities) > 0 else 1.0

    # Clear old scores (Tactical Purge)
    await session.execute(delete(CriticalityScore))

    for i, pkg_id in enumerate(pkg_ids):
        psi = v[i] / max_v
        auth = authorities[i] / max_auth
        hub = hubs[i] / (np.max(hubs) if np.max(hubs) > 0 else 1.0)

        vel = vel_map.get(pkg_id, 0.0)
        # Normalize velocity (capped at 10.0 for scaling)
        vel_norm = min(vel / 10.0, 1.0)

        # Blast Radius reach (Approximated by HITS/Centrality or fetched)
        # For true Br(v), we'd need walk_upstream for all nodes, which is expensive.
        # Instruction says: ln(1 + Br(v)).
        # We'll fetch it using high-speed count for this specimen
        br_res = await session.execute(
            text("""
            SELECT COUNT(DISTINCT v.package_id)
            FROM dependency_edges de
            JOIN package_versions v ON de.parent_version_id = v.id
            WHERE de.child_package_id = :pkg_id
        """),
            {"pkg_id": pkg_id},
        )
        br_count = br_res.scalar() or 0
        reach_comp = math.log(1 + br_count)

        # Final C_idx
        # psi (Eigenvector) is our topological weight (0.50)
        # velocity is 0.20
        # reach (~ln(count)) is 0.30
        c_idx = (0.5 * psi) + (0.2 * vel_norm) + (0.3 * min(reach_comp / 10.0, 1.0))

        score = CriticalityScore(
            package_id=pkg_id,
            centrality_score=float(psi),
            authority_score=float(auth),
            hub_score=float(hub),
            c_idx=float(min(max(c_idx, 0.0), 1.0)),
        )
        session.add(score)

    await session.commit()


async def get_top_critical_nodes(session: AsyncSession, limit: int = 100) -> List[Dict[str, Any]]:
    """Generates the 'Strategic Vision' for the 144Hz HUD."""
    sql = (
        select(Package, CriticalityScore)
        .join(CriticalityScore)
        .order_by(CriticalityScore.c_idx.desc())
        .limit(limit)
    )
    res = await session.execute(sql)
    out = []
    for pkg, score in res.all():
        out.append(
            {
                "name": pkg.name,
                "ecosystem": pkg.ecosystem,
                "c_idx": score.c_idx,
                "authority": score.authority_score,
                "centrality": score.centrality_score,
            }
        )
    return out
