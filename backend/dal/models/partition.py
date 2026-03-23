import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, Float, Index, text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from dal.base import Base


class GraphCommunity(Base):
    """
    Persistent anchor for topologically identified clusters.
    Encapsulates aggregate metrics and hierarchical lineage for supply chain silos.
    """

    __tablename__ = "graph_communities"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        index=True,
    )

    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    modularity_contribution: Mapped[float] = mapped_column(Float, default=0.0)

    node_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_criticality: Mapped[float] = mapped_column(Float, default=0.0)

    hierarchy_level: Mapped[int] = mapped_column(Integer, default=0)
    parent_community_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("graph_communities.id", ondelete="SET NULL"), nullable=True
    )

    last_computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    parent_community = relationship("GraphCommunity", remote_side=[id], backref="sub_communities")


class CommunityMembership(Base):
    """
    Relational binding between package nodes and their primary topological silos.
    Supports soft-weighting for cross-community bridge detection.
    """

    __tablename__ = "community_membership"

    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), primary_key=True
    )
    community_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("graph_communities.id", ondelete="CASCADE"), index=True
    )

    membership_coefficient: Mapped[float] = mapped_column(Float, default=1.0)

    __table_args__ = (Index("ix_membership_community_package", "community_id", "package_id"),)
