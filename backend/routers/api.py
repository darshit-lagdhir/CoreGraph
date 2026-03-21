from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import AsyncSessionLocal
from models import Package
from schemas import PackageSchema, IngestRequestSchema, IngestResponseSchema
from tasks.ingestion import ingest_ecosystem_structure
from worker import celery_app
from redis.asyncio import Redis
from config import settings
import json

api_router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@api_router.get("/packages/{ecosystem}/{name}", response_model=PackageSchema)
async def get_package(ecosystem: str, name: str, db: AsyncSession = Depends(get_db)):
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    cache_key = f"coregraph:pkg:{ecosystem}:{name}"
    cached = await redis_client.get(cache_key)
    
    if cached:
        await redis_client.aclose()
        return PackageSchema.model_validate_json(cached)
        
    result = await db.execute(
        select(Package).where(
            Package.ecosystem == ecosystem,
            Package.name == name
        )
    )
    pkg = result.scalars().first()
    if not pkg:
        await redis_client.aclose()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node unmapped within persistent structures.")
        
    schema_dump = PackageSchema.model_validate(pkg).model_dump_json()
    await redis_client.set(cache_key, schema_dump, ex=3600)
    await redis_client.aclose()
    
    return pkg

@api_router.post("/ingest", response_model=IngestResponseSchema, status_code=status.HTTP_202_ACCEPTED)
async def trigger_ingestion(request: IngestRequestSchema):
    # JWT & Rate Limit validation simulation boundary context
    result = ingest_ecosystem_structure.apply_async(
        args=[request.ecosystem, request.name]
    )
    return IngestResponseSchema(task_id=str(result.id), status="DISPATCHED_TO_BROKER")

@api_router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "state": result.state,
    }
