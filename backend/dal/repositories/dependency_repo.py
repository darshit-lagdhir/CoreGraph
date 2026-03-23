import uuid
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import DependencyEdge, PackageVersion


class DependencyRepository:
    """
    CoreGraph Topological Module.
    Resolves local neighborhoods and dependency graphs for the 3.88M node software ocean.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_local_neighborhood(
        self, package_id: uuid.UUID, depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Retrieves direct dependencies of the latest version of the package.
        Truncates at depth=3 to prevent join explosions. (Task 025.6)
        """
        # 1. Fetch latest version to get its dependencies
        stmt_v = (
            select(PackageVersion.id)
            .where(PackageVersion.package_id == package_id)
            .order_by(PackageVersion.sort_key.desc())
            .limit(1)
        )
        res_v = await self.session.execute(stmt_v)
        version_id = res_v.scalar()

        if not version_id:
            return []

        # 2. Fetch edges
        stmt = select(DependencyEdge).where(DependencyEdge.parent_version_id == version_id)
        res = await self.session.execute(stmt)
        edges = res.scalars().all()

        return [
            {
                "target_package_id": str(e.child_package_id),
                "requirement": e.specifier,
                "is_dev": e.is_development,
                "is_optional": e.is_optional,
            }
            for e in edges
        ]
