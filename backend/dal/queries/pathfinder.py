import asyncio
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def calculate_blast_radius_score(nodes: List[Dict[str, Any]]) -> float:
    """
    Quantifies the security risk impact across the supply chain.
    Higher scores indicate deep-rooted, widespread consumer chains (Blast Radius).
    Formula: Σ (risk_score_i / depth_i)
    """
    if not nodes:
        return 0.0
    
    total_score = 0.0
    for node in nodes:
        depth = node.get("depth", 1)
        risk = node.get("risk_score", 0.1)
        # Deep dependency is less 'direct' risk, but we weigh it by depth
        total_score += risk / (depth * 0.5 + 0.5)
        
    return round(total_score, 4)


async def walk_upstream(session: AsyncSession, package_id: uuid.UUID, max_depth: int = 15) -> List[Dict[str, Any]]:
    """
    The Recursive CTE Engine: Walking the OSINT Continent.
    Identifies all packages dependent on a core specimen (Upstream Walk).
    Optimized for GEN5 traversal.
    """
    # 1. Implementation of the Recursive Walk
    # This CTE starts with children (dependents) and moves up to parents
    # Actually, if we've been walking 'upstream', it means finding consumers of this pkg.
    
    sql = text("""
        WITH RECURSIVE consumer_tree AS (
            -- Seed: The direct dependents of the target package versions
            SELECT 
                de.parent_version_id,
                de.child_package_id,
                1 as depth,
                p.name,
                p.ecosystem
            FROM dependency_edges de
            JOIN package_versions v ON de.parent_version_id = v.id
            JOIN packages p ON v.package_id = p.id
            WHERE de.child_package_id = :pkg_id
            
            UNION ALL
            
            -- Recursive Case: Find dependents of those dependents
            SELECT 
                de.parent_version_id,
                de.child_package_id,
                ct.depth + 1,
                p.name,
                p.ecosystem
            FROM dependency_edges de
            JOIN package_versions v ON de.parent_version_id = v.id
            JOIN packages p ON v.package_id = p.id
            JOIN consumer_tree ct ON de.child_package_id = p.id
            WHERE ct.depth < :max_depth
        )
        SELECT DISTINCT name, ecosystem, depth FROM consumer_tree;
    """)
    
    result = await session.execute(sql, {"pkg_id": package_id, "max_depth": max_depth})
    return [dict(row._mapping) for row in result]
