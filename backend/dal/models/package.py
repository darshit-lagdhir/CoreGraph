import uuid
from datetime import datetime

from dal.base import Base
from sqlalchemy import DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Package(Base):
    """
    Foundational Package Model: The Structural Backbone of CoreGraph's 3.88M node ocean.
    Enforces UUIDv4 primary keys and Composite Uniqueness on (Ecosystem, Name).
    """

    __tablename__ = "packages"

    # UUID Primary Key (Failure 2 Resolution: Moved generation to DB kernel)
    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        index=True,
        unique=True,
        doc="Primary 128-bit identifier for the package entity.",
    )

    # Relationships (Section 2.A)
    versions = relationship(
        "PackageVersion", back_populates="package", cascade="all, delete-orphan"
    )

    # Memory-Aligned String Constraints (Section 3.C)
    ecosystem: Mapped[str] = mapped_column(
        String(32), nullable=False, doc="Registry platform (e.g., NPM, PyPI, Go)."
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="Canonical package name defined by the ecosystem."
    )
    version_latest: Mapped[str | None] = mapped_column(
        String(64), nullable=True, doc="Most recent version string detected."
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        # Composite Uniqueness Encodement (Section 3.B)
        UniqueConstraint("ecosystem", "name", name="uq_package_ecosystem_name"),
        # GIN Trigram Index for fuzzy search (Section 3.B)
        Index(
            "ix_package_name_trgm",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
        # Case-Insensitive Uniqueness (Failure 1 Resolution: Functional Index)
        Index("ix_package_name_lower_unique", func.lower(name), func.lower(ecosystem), unique=True),
    )

    def __repr__(self) -> str:
        return f"<Package(id={self.id}, ecosystem='{self.ecosystem}', name='{self.name}')>"
