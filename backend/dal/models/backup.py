import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import (
    String,
    ForeignKey,
    Integer,
    BigInteger,
    LargeBinary,
    Index,
    text,
    func,
    DateTime,
    Enum as SQLEnum,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from dal.base import Base


class BackupType(str, Enum):
    """The depth of the OSINT snapshot."""

    FULL = "full"
    DIFFERENTIAL = "differential"
    WAL_ARCHIVE = "wal_archive"


class BackupStatus(str, Enum):
    """The integrity state of the forensic replica."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    CORRUPTED = "corrupted"
    PURGED = "purged"


class BackupLedger(Base):
    """
    The Resilience Registry (The Black Box).
    Tracks every physical and logical backup event for the 3.88M node graph.
    Maintains WAL (Write-Ahead Log) sequence continuity for PITR.
    """

    __tablename__ = "backup_ledger"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    backup_type: Mapped[BackupType] = mapped_column(
        SQLEnum(BackupType, name="backup_type_enum"), nullable=False
    )
    status: Mapped[BackupStatus] = mapped_column(
        SQLEnum(BackupStatus, name="backup_status_enum"),
        default=BackupStatus.IN_PROGRESS,
        index=True,
    )

    # THE RECOVERY ANCHORS (PostgreSQL LSN stream pointers)
    start_lsn: Mapped[str] = mapped_column(String(64), nullable=False)
    end_lsn: Mapped[Optional[str]] = mapped_column(String(64))

    # STORAGE TELEMETRY (Gen5 NVMe throughput metrics)
    total_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    compressed_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)

    # INTEGRITY SIGNATURES (Task 016 verification)
    manifest_hash: Mapped[Optional[bytes]] = mapped_column(LargeBinary(32))

    # CLOUD SYNCHRONIZATION (Supabase Disaster Recovery)
    is_cloud_synced: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_backup_timeline_v2", created_at.desc(), backup_type),
        Index("ix_lsn_pointer_v2", start_lsn, end_lsn),
    )
