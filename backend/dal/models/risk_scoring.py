import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Float, Integer, Index, text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from dal.base import Base


class RiskScoringIndex(Base):
    """
    CoreGraph Intelligence Surface.
    Stores pre-calculated multi-vector risk indices ($R_{idx}$) for all 3.88M nodes.
    Optimized for high-velocity real-time recoloring in the 144Hz HUD.
    """

    __tablename__ = "risk_scoring_index"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )

    # INDIVIDUAL NORMALIZED RISK VECTORS [0.0 - 1.0]
    v_topo: Mapped[float] = mapped_column(Float, default=0.0)  # Criticality (Task 013)
    v_beh: Mapped[float] = mapped_column(Float, default=0.0)  # Contributor Velocity (Task 004)
    v_str: Mapped[float] = mapped_column(Float, default=0.0)  # Blast Radius (Task 011)
    v_temp: Mapped[float] = mapped_column(Float, default=0.0)  # Temporal Recency (Task 012)
    v_tel: Mapped[float] = mapped_column(Float, default=1.0)  # Node Vitality (Task 017)

    # THE AGGREGATED OSINT RISK SCORE
    r_idx: Mapped[float] = mapped_column(Float, index=True, default=0.0)

    # ANALYST OVERRIDE MULTIPLIER (Task 020)
    manual_risk_multiplier: Mapped[float] = mapped_column(Float, default=1.0)

    last_recalculated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_r_idx_ranking", r_idx.desc()),
        # Composite index for "Hot Risk" high-criticality filtering.
        Index("ix_risk_surface_search", r_idx, v_topo, v_beh),
    )


class HeatMapGrid(Base):
    """
    Spatial OSINT Aggregation Layer.
    Stores gridded threat density cells (32x32x32) for global ecosystem views.
    Enables zero-latency rendering of graph hotspots on the 144Hz HUD.
    """

    __tablename__ = "heatmap_grid"

    # Grid Cell Coordinates (Spatial Hash)
    grid_x: Mapped[int] = mapped_column(Integer, primary_key=True)
    grid_y: Mapped[int] = mapped_column(Integer, primary_key=True)
    grid_z: Mapped[int] = mapped_column(Integer, primary_key=True)

    # AGGREGATED METRICS
    node_density: Mapped[int] = mapped_column(Integer, default=0)
    mean_r_idx: Mapped[float] = mapped_column(Float, default=0.0)
    max_r_idx: Mapped[float] = mapped_column(Float, default=0.0)  # Peak threat detection

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
