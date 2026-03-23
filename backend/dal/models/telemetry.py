import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, Float, Index, text, func, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from dal.base import Base


class NodeTelemetry(Base):
    """
    High-frequency vitality log for OSINT supply chain nodes.
    Tracks structural integrity and metadata coverage to detect data decay.
    """

    __tablename__ = "node_telemetry"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # TELEMETRY VECTORS
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    completeness_score: Mapped[float] = mapped_column(Float, default=1.0)
    is_structurally_sound: Mapped[int] = mapped_column(Integer, default=1)  # 1=True, 0=False

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    __table_args__ = (Index("ix_telemetry_package_time_vitality", "package_id", "recorded_at"),)


class HealthAnomaly(Base):
    """
    Forensic record of structural graph failures.
    Flagged by the Autonomous Sweeper to trigger database triage events.
    """

    __tablename__ = "health_anomalies"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), index=True
    )

    anomaly_type: Mapped[str] = mapped_column(String(64))  # GHOST_VERSION, ZOMBIE_EDGE
    severity: Mapped[float] = mapped_column(Float, default=0.5)

    details: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'"))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
