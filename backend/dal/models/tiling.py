import uuid
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import String, ForeignKey, Integer, Float, Index, text, func, DateTime, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from dal.base import Base

class SummaryNode(Base):
    """
    Hierarchical aggregation of topological entities.
    Enables multi-scale detail-performance balancing for global-scale HUD visualization.
    """
    __tablename__ = "summary_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    
    # 0 = Global (Ecosystem), 1 = Regional (Community), 2 = Local (Cluster)
    lod_level: Mapped[int] = mapped_column(Integer, index=True)
    
    pos_x: Mapped[float] = mapped_column(Float)
    pos_y: Mapped[float] = mapped_column(Float)
    pos_z: Mapped[float] = mapped_column(Float)
    
    total_nodes_contained: Mapped[int] = mapped_column(Integer)
    aggregate_criticality: Mapped[float] = mapped_column(Float)
    representative_risk_score: Mapped[float] = mapped_column(Float)
    
    community_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("graph_communities.id", ondelete="SET NULL"), nullable=True, index=True
    )

    label_metadata: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'"))

class VisualizationTile(Base):
    """
    Spatial partition for high-velocity telemetry streaming.
    Utilizes Morton-encoded indexing for O(1) frustum-based retrieval on the i9-13980hx.
    """
    __tablename__ = "visualization_tiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    
    tile_index: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    zoom_level: Mapped[int] = mapped_column(Integer, index=True)
    
    min_x: Mapped[float] = mapped_column(Float)
    max_x: Mapped[float] = mapped_column(Float)
    min_y: Mapped[float] = mapped_column(Float)
    max_y: Mapped[float] = mapped_column(Float)
    min_z: Mapped[float] = mapped_column(Float)
    max_z: Mapped[float] = mapped_column(Float)

    tile_data: Mapped[bytes] = mapped_column(LargeBinary)

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
