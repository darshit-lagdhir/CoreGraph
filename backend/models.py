import uuid
from datetime import datetime
from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
    Numeric,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    ecosystem: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    latest_version: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    license: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    __table_args__ = (UniqueConstraint("ecosystem", "name", name="uix_ecosystem_name"),)


class DependencyEdge(Base):
    __tablename__ = "dependencies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_requirement: Mapped[str | None] = mapped_column(String, nullable=True)
    is_direct: Mapped[bool] = mapped_column(Boolean, default=True)


class MaintainerHealth(Base):
    __tablename__ = "maintainer_health"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    github_repo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    commit_velocity_30d: Mapped[int] = mapped_column(Integer, default=0)
    active_maintainers_count: Mapped[int] = mapped_column(Integer, default=0)
    last_commit_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0)


class FinancialHealth(Base):
    __tablename__ = "financial_health"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    funding_platform: Mapped[str | None] = mapped_column(String, nullable=True)
    platform_slug: Mapped[str | None] = mapped_column(String, nullable=True)
    annual_budget_usd: Mapped[float] = mapped_column(Numeric(precision=18, scale=2), default=0.0)
    current_balance_usd: Mapped[float] = mapped_column(Numeric(precision=18, scale=2), default=0.0)
    is_commercially_backed: Mapped[bool] = mapped_column(Boolean, default=False)
