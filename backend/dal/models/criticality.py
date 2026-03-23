import uuid
from datetime import datetime
from sqlalchemy import Float, ForeignKey, Index, text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from dal.base import Base


class CriticalityScore(Base):
    """
    The Strategic Intelligence Vault.
    Stores the pre-computed 'Security Credit Score' for every node.
    """

    __tablename__ = "criticality_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        index=True,
    )

    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )

    # INDIVIDUAL VECTORS (Task 013 Domain)
    centrality_score: Mapped[float | None] = mapped_column(Float, default=0.0)
    authority_score: Mapped[float | None] = mapped_column(Float, default=0.0)
    hub_score: Mapped[float | None] = mapped_column(Float, default=0.0)

    # THE QUANTIZED OUTPUT ($C_{idx}$)
    c_idx: Mapped[float | None] = mapped_column(Float, index=True, default=0.0)

    last_computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # RELATIONSHIPS
    package = relationship("Package")

    __table_args__ = (
        # Index for the AI's "Top 100" queries (Pruning Protocol)
        Index("ix_c_idx_desc", c_idx.desc()),
    )
