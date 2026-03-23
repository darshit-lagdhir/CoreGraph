import uuid
from typing import Any
from sqlalchemy import select, func
from dal.models.graph import Package
from dal.models.partition import CommunityMembership
from sqlalchemy.ext.asyncio import AsyncSession


class PartitionRepository:
    """
    Sub-Graph Isolation Module.
    Managing high-fidelity risk silos and multi-tenant workspace segregation.
    (CoreGraph Protocol).
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def apply_segmentation(self, query, community_id: uuid.UUID):
        """
        Dynamically injects join-based isolation to restrict query scope
        to the assigned community partition.
        """
        return query.join(CommunityMembership, CommunityMembership.package_id == Package.id).where(
            CommunityMembership.community_id == community_id
        )

    async def get_total_segment_mass(self, community_id: uuid.UUID) -> int:
        """Quantifies the topological volume of the active OSINT silo."""
        res = await self.session.execute(
            select(func.count(CommunityMembership.package_id)).where(
                CommunityMembership.community_id == community_id
            )
        )
        return res.scalar() or 0
