from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any


async def get_blast_radius(
    session: AsyncSession, target_id: str, max_depth: int = 10
) -> List[Dict[str, Any]]:
    """
    Executes a high-performance recursive traversal to identify all upstream
    packages affected by a compromised target node.

    Optimized for the i9-13980hx parallel execution model.
    """
    query = text("""
        WITH RECURSIVE blast_radius AS (
            -- BASE CASE: Find immediate parents of the compromised child
            SELECT
                parent_version_id,
                child_package_id,
                1 AS depth
            FROM dependency_edges
            WHERE child_package_id = :target_id
              AND is_development = False

            UNION ALL

            -- RECURSIVE STEP: Find versions that depend on the package of the version from the previous step
            SELECT
                de.parent_version_id,
                de.child_package_id,
                br.depth + 1
            FROM dependency_edges de
            INNER JOIN package_versions pv ON de.child_package_id = pv.package_id
            INNER JOIN blast_radius br ON pv.id = br.parent_version_id
            WHERE br.depth < :limit
        )
        SELECT DISTINCT
            p.name as package_name,
            pv.version_string,
            br.depth
        FROM blast_radius br
        JOIN package_versions pv ON br.parent_version_id = pv.id
        JOIN packages p ON pv.package_id = p.id
        ORDER BY br.depth ASC;
    """)

    result = await session.execute(query, {"target_id": target_id, "limit": max_depth})
    return [dict(row) for row in result.mappings().all()]
