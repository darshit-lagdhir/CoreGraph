import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import Package, PackageVersion
from dal.models.temporal import GraphSnapshot, NodeDelta


class TemporalRepository:
    """The Persistence Engine for Task 012 Snapshots."""

    async def create_snapshot(self, session: AsyncSession, name: str) -> GraphSnapshot:
        snap = GraphSnapshot(name=name)
        session.add(snap)
        await session.flush()
        return snap

    async def record_node_delta(self, session: AsyncSession, snapshot_id: uuid.UUID, node_id: uuid.UUID, change_type: str, diff: Dict[str, Any]) -> NodeDelta:
        delta = NodeDelta(snapshot_id=snapshot_id, node_id=node_id, change_type=change_type, diff_payload=diff)
        session.add(delta)
        return delta

    async def get_package_at_time(self, session: AsyncSession, name: str, timestamp: datetime) -> Optional[Package]:
        """The 'Time Machine' lookup for OSINT historical audits."""
        query = select(Package).where(
            and_(
                Package.name == name,
                Package.valid_from <= timestamp,
                (Package.valid_to == None) | (Package.valid_to >= timestamp)
            )
        )
        result = await session.execute(query)
        return result.scalars().first()


class DiffEngine:
    """The Algebraic Engine for Graph Delta Calculations."""
    
    def calculate_temporal_delta(self, snap_a: Dict[str, Any], snap_b: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simulation of the Task 012 Difference Engine (CoreGraph Algorithm)
        deltas = []
        for id, node in snap_b.items():
            if id not in snap_a:
                deltas.append({"id": id, "type": "ADDED", "new": node})
            elif snap_a[id] != node:
                deltas.append({"id": id, "type": "UPDATED", "old": snap_a[id], "new": node})
        return deltas
