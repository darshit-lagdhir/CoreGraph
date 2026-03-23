import uuid
from typing import Any
from sqlalchemy import select
from dal.models.graph import Package
from dal.models.partition import CommunityMembership

class SegmentedDataAccess:
    """
    Sub-Graph Isolation Protocol: Managing high-fidelity risk silos.
    Enforces multi-tenant workspace segregation to minimize L3 cache thrashing.
    """
    def __init__(self, community_id: uuid.UUID):
        self.community_id = community_id

    def apply_segmentation(self, query):
        """
        Dynamically injects join-based isolation to restrict query scope
        to the assigned community partition.
        """
        return query.join(
            CommunityMembership, 
            CommunityMembership.package_id == Package.id
        ).where(CommunityMembership.community_id == self.community_id)

    async def get_total_segment_mass(self, session) -> int:
        """Quantifies the topological volume of the active OSINT silo."""
        res = await session.execute(
            select(func.count(CommunityMembership.package_id))
            .where(CommunityMembership.community_id == self.community_id)
        )
        return res.scalar() or 0
