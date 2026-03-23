import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import String, ForeignKey, Float, Integer, Index, text, func, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from dal.base import Base

class AlertSeverity(str, Enum):
    """Classification of the security signal's intensity."""
    INFO = "info"       # Metadata drift / Baseline updates
    WARNING = "warning" # Anomalous velocity or structural changes
    CRITICAL = "critical" # Immediate threshold breach on foundational nodes
    EMERGENCY = "emergency" # Confirmed malicious intelligence (Task 020)

class AlertEvent(Base):
    """
    CoreGraph Sentinel Notification.
    A push-based proactive alarm generated when $R_{idx}$ or behavioral delta 
    crosses ecosystem-aware critical thresholds.
    """
    __tablename__ = "alert_events"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    
    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    severity: Mapped[AlertSeverity] = mapped_column(
        SQLEnum(AlertSeverity, name="alert_severity_type"), 
        default=AlertSeverity.INFO,
        index=True
    )
    
    # SYSTEM STATE SNAPSHOT ($T_{crit}$ Baseline)
    risk_snapshot: Mapped[float] = mapped_column(Float, nullable=False)
    criticality_snapshot: Mapped[float] = mapped_column(Float, nullable=False)
    
    # FORENSIC TRIGGER CONTEXT
    # Explicit indicators for AI-assisted analytical drill-down (Module 3)
    trigger_payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # OPERATIONAL WORKFLOW
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[Optional[uuid.UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        index=True
    )

    __table_args__ = (
        # Optimization for the "Active Crisis" HUD dashboard (Task 022.3)
        Index("ix_active_alert_emergencies", "severity", "is_acknowledged"),
        # Historical search index for auditing specific package breeches
        Index("ix_package_alert_history", "package_id", text("created_at DESC")),
    )
