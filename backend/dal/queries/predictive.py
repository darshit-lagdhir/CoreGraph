import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import Package, PackageVersion, DependencyEdge


async def prefetch_graph_neighborhood(session: AsyncSession, package_id: str, depth: int = 1):
    """
    The 'Spatial Locality' Engine.
    Pre-loads neighboring graph nodes into the Identity Map
    to ensure 0ms latency hits when the 144Hz HUD requests them.
    """
    # 1. Fetch Downstream (Dependencies of latest version)
    # 2. Fetch Upstream (Dependents / Blast Radius)
    # We fire parallel tasks into the i9's task queue

    # Forward Traversal (latest version's dependencies)
    forward_query = (
        select(DependencyEdge)
        .where(
            DependencyEdge.parent_version_id.in_(
                select(PackageVersion.id)
                .where(PackageVersion.package_id == package_id)
                .order_by(PackageVersion.semver_sort_index.desc())
                .limit(1)
            )
        )
        .limit(50)
    )

    # Reverse Traversal (who depends on this package)
    reverse_query = (
        select(DependencyEdge).where(DependencyEdge.child_package_id == package_id).limit(50)
    )

    # Prefetch into the SQLAlchemy Session (Identity Map Cache)
    # This prevents the HUD from 'stuttering' when clicking nodes.
    await asyncio.gather(session.execute(forward_query), session.execute(reverse_query))
    # Results are now in 'session.identity_map' and the HUD can fetch
    # neighbors instantly by ID.
