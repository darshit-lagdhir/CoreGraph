import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, LargeBinary, Index, text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID, BYTEA
from dal.base import Base


class MerkleNode(Base):
    """
    Cryptographic building block for hierarchical graph signatures.
    Stores SHA-256 hashes in a persistent binary tree for supply chain verification.
    """

    __tablename__ = "merkle_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    # 0 = Root (The Signature), Max = Leaf (The Node Data)
    tree_level: Mapped[int] = mapped_column(Integer, index=True)

    node_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)

    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("merkle_nodes.id", ondelete="CASCADE"), nullable=True, index=True
    )

    package_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("packages.id", ondelete="SET NULL"), nullable=True, index=True
    )

    parent = relationship("MerkleNode", remote_side=[id], backref="children")


class AuditBlock(Base):
    """
    Immutable ledger entry recording graph-wide state mutations.
    Enforces a cryptographic chain of custody for forensic OSINT evidence.
    """

    __tablename__ = "audit_blocks"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    prev_block_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    current_root_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)

    # Traceability to the originating event
    event_id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), unique=True, nullable=False
    )

    # Master signature for forensic non-repudiation
    signature: Mapped[bytes] = mapped_column(BYTEA, nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    __table_args__ = (Index("ix_audit_chain_state", "timestamp", "prev_block_hash"),)
