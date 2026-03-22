import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from dal.base import Base

class GraphSnapshot(Base):
    """Encapsulates a temporal slice of the global ecosystem."""
    __tablename__ = "graph_snapshots"
    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    node_deltas = relationship("NodeDelta", back_populates="snapshot", cascade="all, delete-orphan")

class NodeDelta(Base):
    """Captures structural mutation of a Package or Version over time."""
    __tablename__ = "node_deltas"
    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    snapshot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("graph_snapshots.id", ondelete="CASCADE"), index=True)
    node_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), index=True)
    change_type: Mapped[str] = mapped_column(String(16)) # ADDED, REMOVED, UPDATED
    diff_payload: Mapped[dict] = mapped_column(JSONB)
    snapshot = relationship("GraphSnapshot", back_populates="node_deltas")

class EdgeDelta(Base):
    """Captures mutation of the supply chain dependency edges."""
    __tablename__ = "edge_deltas"
    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    snapshot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("graph_snapshots.id", ondelete="CASCADE"), index=True)
    edge_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), index=True)
    change_type: Mapped[str] = mapped_column(String(16))
    diff_payload: Mapped[dict] = mapped_column(JSONB)
