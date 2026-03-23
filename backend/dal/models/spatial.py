import uuid
from typing import Any
from sqlalchemy import Column, Integer, String, ForeignKey, Index, text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from dal.base import Base

from sqlalchemy.types import UserDefinedType


class CubeType(UserDefinedType):
    def get_col_spec(self, **kw):
        return "cube"


class PointType(UserDefinedType):
    def get_col_spec(self, **kw):
        return "point"


class PackageSpatialIndex(Base):
    """
    Multidimensional Search Anchor for the 3.88M node graph.
    Maps package metadata into a (Criticality, Risk, Recency) 3D coordinate space.
    Enables surgical O(log N) extraction of security sub-graphs.
    """

    __tablename__ = "package_spatial_index"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )

    package_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("packages.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )

    # 3D RISK VECTOR (Stored as PostgreSQL 'cube' type)
    risk_vector: Mapped[Any] = mapped_column(CubeType(), nullable=False)

    # GEOGRAPHICAL ORIGIN (Stored as PostgreSQL 'point' type)
    origin_location: Mapped[Any] = mapped_column(PointType(), nullable=True)

    __table_args__ = (
        # THE GiST INDEX: Multi-dimensional R-Tree for risk-box intersections.
        # Optimized for i9-13980hx SIMD search logic via the 'cube' operator.
        Index("ix_package_risk_space", "risk_vector", postgresql_using="gist"),
        # SPATIAL INDEX for Jurisdictional search boundaries (e.g. EU/US exports).
        Index("ix_package_geo_origin", "origin_location", postgresql_using="gist"),
    )
