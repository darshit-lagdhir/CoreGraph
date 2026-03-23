import uuid
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import String, ForeignKey, Integer, Float, Index, text, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from dal.base import Base


class Workspace(Base):
    """
    Collaborative Investigation Container.
    Isolates specific OSINT missions and team environments in the 3.88M node graph.
    """

    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024))

    owner_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GraphTag(Base):
    """
    Semantic OSINT Label (LWW-Element-Set CRDT).
    Conflict-free convergence point for collaborative node/version tagging.
    """

    __tablename__ = "graph_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )

    # POLYMORPHIC ANCHOR
    target_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), index=True)
    target_type: Mapped[str] = mapped_column(String(32))  # 'PACKAGE' or 'VERSION'

    label: Mapped[str] = mapped_column(String(64), index=True)

    # CRDT CONVERGENCE FIELDS
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    lamport_timestamp: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True))

    __table_args__ = (Index("ix_tag_resolution_crdt", "target_id", "label", "lamport_timestamp"),)


class ForensicNote(Base):
    """
    Investigative Detail with Immutable Delta History.
    Rich-text forensic evidence with temporal version control and JSONB patching.
    """

    __tablename__ = "forensic_notes"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    target_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), index=True)

    # DELTA TRACKING ENGINE
    content: Mapped[str] = mapped_column("TEXT", nullable=False)
    history: Mapped[List[dict]] = mapped_column(JSONB, server_default=text("'[]'"))

    author_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
