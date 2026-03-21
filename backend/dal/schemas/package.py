import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PackageBase(BaseModel):
    """Foundational Pydantic v2 reflection for type-safe data transit."""

    ecosystem: str = Field(..., max_length=32)
    name: str = Field(..., max_length=255)
    version_latest: str | None = Field(None, max_length=64)


class PackageCreate(PackageBase):
    pass


class PackageRead(PackageBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
