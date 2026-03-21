import uuid
from datetime import datetime

from dal.base import Base
from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PackageVersion(Base):
    """
    Chronicle of Evolution: The versioning sub-structure for CoreGraph releases.
    Stores metadata in JSONB and implements relational version chains (linked-list DAG).
    """

    __tablename__ = "package_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Primary 128-bit identifier for the release entity.",
    )

    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="Reference to the parent package entity (one-to-many).",
    )

    version_string: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="The raw version identifier (e.g., '1.2.4-beta', 'v0.0.0-2021...').",
    )

    # SemVer Sort Logic (Section 3.B and Failure 1 Resolution)
    semver_sort_index: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        doc="BIGINT sortable representation of the version for 144Hz HUD rendering.",
    )

    # JSONB Metadata Vault (Section 2.C and Failure 2 Resolution: Selective Persistence via TOAST)
    metadata_extra: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Binary-JSON storage for ecosystem-specific OSINT metadata (NPM/PyPI/Go).",
    )

    # Relational Version Chains (Section 4.A and Failure 3 Resolution: Self-referential FK)
    previous_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("package_versions.id", ondelete="SET NULL"),
        nullable=True,
        doc="Pointer to the direct predecessor for lineage traversal (Linked-List Topology).",
    )

    release_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        doc="UTC-aware timestamp of the package release.",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships for ORM traversal
    package = relationship("Package", back_populates="versions")
    previous_version = relationship("PackageVersion", remote_side=[id])

    __table_args__ = (
        # Composite Uniqueness and Version Integrity (Section 2.B)
        UniqueConstraint("package_id", "version_string", name="uq_package_version_string"),
        # GIN Index for JSONB Metadata containment searching (Section 2.C)
        Index("ix_package_version_metadata_gin", "metadata_extra", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return (
            f"<PackageVersion(id={self.id}, ver='{self.version_string}', pkg_id={self.package_id})>"
        )
