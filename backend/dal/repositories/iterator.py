import uuid
from typing import AsyncGenerator, List, Dict, Any, Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession


class GraphWalkIterator:
    """The High-Velocity Recursive Iterator for Task 011 Blast Radius Audits."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_direct_dependents(self, package_id: uuid.UUID) -> List[uuid.UUID]:
        """Atomically fetches the first layer of the consumer chain."""
        sql = text("""
            SELECT DISTINCT v.package_id
            FROM dependency_edges de
            JOIN package_versions v ON de.parent_version_id = v.id
            WHERE de.child_package_id = :pkg_id
        """)
        result = await self.session.execute(sql, {"pkg_id": package_id})
        return [row[0] for row in result]

    async def walk_total_consumers(self, package_id: uuid.UUID, max_depth: int = 5) -> int:
        """The 'Blast Radius' Quantization (Task 011 competitive protocol)."""
        visited = {package_id}
        queue = [(package_id, 0)]
        count = 0

        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            dependents = await self.get_direct_dependents(current)
            for deb in dependents:
                if deb not in visited:
                    visited.add(deb)
                    queue.append((deb, depth + 1))
                    count += 1
        return count
