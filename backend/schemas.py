from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

class PackageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    ecosystem: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    latest_version: str | None = None
    created_at: datetime

class IngestRequestSchema(BaseModel):
    ecosystem: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)

class IngestResponseSchema(BaseModel):
    task_id: str
    status: str
