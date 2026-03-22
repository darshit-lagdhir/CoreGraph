import uuid
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, UniqueConstraint, func, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from dal.base import Base

class Package(Base):
    """
    Foundational Package Model: The Structural Backbone of CoreGraph.
    """
    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        index=True,
    )

    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    versions = relationship("PackageVersion", back_populates="package", cascade="all, delete-orphan")
    dependents = relationship("DependencyEdge", back_populates="child_package")
    maintainer_metrics: Mapped[list["MaintainerMetrics"]] = relationship(
        "MaintainerMetrics", back_populates="package", cascade="all, delete-orphan"
    )

    ecosystem: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version_latest: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("ecosystem", "name", name="uq_package_ecosystem_name"),
        Index("ix_package_name_lower_unique", func.lower(name), func.lower(ecosystem), unique=True),
        Index("uq_package_current_state", "ecosystem", "name", postgresql_where=valid_to.is_(None), unique=True),
    )

class PackageVersion(Base):
    """
    Chronicle of Evolution: The versioning sub-structure for CoreGraph releases.
    """
    __tablename__ = "package_versions"

    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True)

    version_string: Mapped[str] = mapped_column(String(128), nullable=False)
    
    semver_sort_index: Mapped[int | None] = mapped_column(BigInteger, index=True)
    metadata_extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    previous_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("package_versions.id", ondelete="SET NULL"), nullable=True)

    # SemVer components (Task 009)
    version_major: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    version_minor: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    version_patch: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    version_prerelease: Mapped[str | None] = mapped_column(String(64))
    version_build: Mapped[str | None] = mapped_column(String(64))
    sort_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, default="00000.00000.00000")
    
    is_stable: Mapped[bool] = mapped_column(sa.Boolean, server_default=sa.text("true"), nullable=False)
    release_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    package = relationship("Package", back_populates="versions")
    dependencies = relationship("DependencyEdge", back_populates="parent_version", cascade="all, delete-orphan")
    previous_version = relationship("PackageVersion", remote_side=[id], backref="next_versions")

    __table_args__ = (
        UniqueConstraint("package_id", "version_string", name="uq_package_version_string"),
    )

class DependencyEdge(Base):
    """
    The directed relationship connecting versions to their target package requirements.
    """
    __tablename__ = "dependency_edges"

    id: Mapped[uuid.UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    parent_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("package_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    child_package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True)

    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    specifier: Mapped[str] = mapped_column(String(128), nullable=False)
    is_development: Mapped[bool] = mapped_column(Boolean, default=False, server_default=sa.text("false"))
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, server_default=sa.text("false"))

    # Relationships
    parent_version = relationship("PackageVersion", back_populates="dependencies")
    child_package = relationship("Package", back_populates="dependents")

    __table_args__ = (
        Index("ix_dependency_forward_traversal", "parent_version_id", "child_package_id", "is_development"),
        Index("ix_dependency_reverse_traversal", "child_package_id", "parent_version_id", "is_development"),
    )
