import uuid
import logging
from typing import List, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.annotation import GraphTag

class MutationRepository:
    """
    CoreGraph Collaborative Module.
    Manages CRDT-based tag convergence and forensic note history.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def apply_tag_crdt(self, workspace_id: uuid.UUID, target_id: uuid.UUID, target_type: str, label: str, user_id: uuid.UUID, is_deleted: bool = False, lamport: int = 0):
        """
        Idempotent CRDT tagging for collaborative OSINT.
        Enforces Last-Write-Wins (LWW) convergence via Lamport timestamps. (Task 020).
        """
        stmt = (
            select(GraphTag)
            .where(GraphTag.workspace_id == workspace_id, GraphTag.target_id == target_id, GraphTag.label == label)
        )
        res = await self.session.execute(stmt)
        existing = res.scalars().first()

        if existing:
            if lamport > existing.lamport_timestamp:
                existing.is_deleted = is_deleted
                existing.lamport_timestamp = lamport
                existing.user_id = user_id
        else:
            new_tag = GraphTag(
                workspace_id=workspace_id,
                target_id=target_id,
                target_type=target_type,
                label=label,
                user_id=user_id,
                is_deleted=is_deleted,
                lamport_timestamp=lamport
            )
            self.session.add(new_tag)

    async def get_resolved_tag_set(self, workspace_id: uuid.UUID, target_id: uuid.UUID) -> Set[str]:
        """Retrieves the set of active (non-deleted) tags for a node."""
        stmt = (
            select(GraphTag.label)
            .where(GraphTag.workspace_id == workspace_id, GraphTag.target_id == target_id, GraphTag.is_deleted == False)
        )
        res = await self.session.execute(stmt)
        return set(res.scalars().all())
