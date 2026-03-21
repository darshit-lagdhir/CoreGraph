import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean, Index, text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from dal.base import Base


class DependencyEdge(Base):
    """
    The core Graph Edge model for CoreGraph.
    Represents a directed relationship where 'parent_version' depends on 'child_package'.

    This table is designed for sparse storage of 100M+ edges with bidirectional
    traversal velocity optimized for the i9-13980hx workstation.
    """

    __tablename__ = "dependency_edges"

    # Primary Key: UUIDv4 ensures zero collisions in distributed OSINT ingestion
    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc="Primary 128-bit identifier for the directed edge.",
    )

    # THE SOURCE NODE (The Parent: a specific version that HAS the dependency)
    parent_version_id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("package_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="The specific version ID that declares this dependency.",
    )

    # THE TARGET NODE (The Child: the package being required)
    child_package_id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("packages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="The ID of the package required by the parent node.",
    )

    # SEMANTIC METADATA
    specifier: Mapped[str] = mapped_column(
        String(128), nullable=False, doc="The raw SemVer range (e.g., '^1.2.3', '>=2.0.0')."
    )

    is_development: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        doc="True if this is a devDependency (filterable in Lite Mode).",
    )

    is_optional: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        doc="True if the dependency is non-critical for core functionality.",
    )

    # TELEMETRY AND AUDIT
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Timestamp of initial edge discovery by the crawler.",
    )

    # Relationships for ORM graph walking
    parent_version = relationship("PackageVersion", back_populates="dependencies")
    child_package = relationship("Package", back_populates="dependents")

    # --- THE DUAL B-TREE INDEXING MANDATE ---
    # Enables Index-Only Scans for Forward and Reverse traversal vectors.
    __table_args__ = (
        # INDEX 1: FORWARD TRAVERSAL (Downstream resolution)
        Index(
            "ix_dependency_forward_traversal",
            "parent_version_id",
            "child_package_id",
            "is_development",
            postgresql_using="btree",
        ),
        # INDEX 2: REVERSE TRAVERSAL (Upstream / Blast Radius calculations)
        Index(
            "ix_dependency_reverse_traversal",
            "child_package_id",
            "parent_version_id",
            "is_development",
            postgresql_using="btree",
        ),
    )

    def __repr__(self) -> str:
        return f"<DependencyEdge(id={self.id}, parent_ver={self.parent_version_id}, child_pkg={self.child_package_id})>"
