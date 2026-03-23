import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from sqlalchemy import (
    String,
    ForeignKey,
    Float,
    Integer,
    LargeBinary,
    Index,
    text,
    func,
    DateTime,
    Enum as SQLEnum,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from dal.base import Base


class ExportFormat(str, Enum):
    """Forensic report exchange standards."""

    CYCLONEDX_JSON = "cyclonedx_json"
    SPDX_TAG_VALUE = "spdx_tag_value"
    COREGRAPH_FORENSIC = "cgbundle"  # Signed, Zstd-compressed OSINT pack
    PDF_SUMMARY = "pdf_summary"  # Human-readable analyst evidence


class ExportStatus(str, Enum):
    """Lifecycle tracking for high-latency artifact generation."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportJob(Base):
    """
    Evidence Export Registry.
    Tracks the lifecycle of surgical graph transformations for forensic SBOMs.
    """

    __tablename__ = "export_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )

    requestor_id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), index=True)
    format: Mapped[ExportFormat] = mapped_column(
        SQLEnum(ExportFormat, name="export_format_type"), nullable=False
    )
    status: Mapped[ExportStatus] = mapped_column(
        SQLEnum(ExportStatus, name="export_status_type"), default=ExportStatus.PENDING, index=True
    )

    # SCOPE TARGETING (Task 019 Extraction Logic)
    scope_query: Mapped[Optional[str]] = mapped_column(String(1024))

    # ARTIFACT PERSISTENCE
    file_path: Mapped[Optional[str]] = mapped_column(String(512))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    sha256_checksum: Mapped[Optional[bytes]] = mapped_column(LargeBinary(32))

    # TELEMETRY AND AUDIT
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (Index("ix_export_job_lifecycle", status, started_at.desc()),)


class ExportArtifact(Base):
    """
    Forensic Artifact Registry.
    Maintains an immutable record of all signed bundles for court-admissible OSINT audits.
    """

    __tablename__ = "export_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("export_jobs.id"), unique=True, nullable=False
    )

    # INTEGRITY ANCHORS (Task 016 Merkle Root)
    merkle_root_at_export: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)

    # CRYPTOGRAPHIC SIGNATURE (Ed25519)
    digital_signature: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
