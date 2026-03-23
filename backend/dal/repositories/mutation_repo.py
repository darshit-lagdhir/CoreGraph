import uuid
from typing import List, Optional
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.annotation import GraphTag, ForensicNote


async def apply_tag_crdt(
    session: AsyncSession,
    workspace_id: uuid.UUID,
    target_id: uuid.UUID,
    target_type: str,
    label: str,
    user_id: uuid.UUID,
    is_deleted: bool,
    lamport: int,
) -> GraphTag:
    """
    Implements LWW-Element-Set (Last-Write-Wins) Tagging.
    Ensures non-blocking convergence across concurrentOSINT workstations.
    """
    # 1. Atomic Upsert Simulation (O(1) conflict resolution)
    # If the incoming lamport_timestamp is higher than existing, update.
    # Otherwise, ignore (outdated mutation).

    stmt = select(GraphTag).where(
        GraphTag.target_id == target_id,
        GraphTag.label == label,
        GraphTag.workspace_id == workspace_id,
    )
    res = await session.execute(stmt)
    existing = res.scalar_one_or_none()

    if existing:
        if lamport > existing.lamport_timestamp:
            existing.is_deleted = is_deleted
            existing.lamport_timestamp = lamport
            existing.user_id = user_id
        return existing

    # New Tag Entry
    tag = GraphTag(
        workspace_id=workspace_id,
        target_id=target_id,
        target_type=target_type,
        label=label,
        user_id=user_id,
        is_deleted=is_deleted,
        lamport_timestamp=lamport,
    )
    session.add(tag)
    return tag


async def get_resolved_tag_set(
    session: AsyncSession, workspace_id: uuid.UUID, target_id: uuid.UUID
) -> List[str]:
    """
    Returns the final converged tag labels for a given node.
    Filters out 'Removed' elements according to CRDT sets.
    """
    stmt = select(GraphTag.label).where(
        GraphTag.target_id == target_id,
        GraphTag.workspace_id == workspace_id,
        GraphTag.is_deleted == False,
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())
