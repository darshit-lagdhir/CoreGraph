from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class PackageSchema(BaseModel):
    id: UUID
    ecosystem: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    latest_version: str | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class IngestRequestSchema(BaseModel):
    ecosystem: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)

class IngestResponseSchema(BaseModel):
    task_id: str
    status: str
