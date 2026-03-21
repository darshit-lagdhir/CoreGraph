import time
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from redis.asyncio import Redis

from config import settings
from database import engine
from worker import celery_app

app = FastAPI(title="CoreGraph API Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Execute raw system ping against isolated infrastructure."""
    response_data = {
        "status": "healthy",
        "database_latency_ms": 0,
        "redis_latency_ms": 0,
        "celery_serializer_secure": False
    }

    start_db = time.perf_counter()
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "component": "database", "detail": str(e)}
        )
    response_data["database_latency_ms"] = round((time.perf_counter() - start_db) * 1000, 2)

    start_redis = time.perf_counter()
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.aclose()
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "component": "redis", "detail": str(e)}
        )
    response_data["redis_latency_ms"] = round((time.perf_counter() - start_redis) * 1000, 2)

    if (celery_app.conf.task_serializer == "json" and 
        celery_app.conf.result_serializer == "json" and 
        "json" in celery_app.conf.accept_content):
        response_data["celery_serializer_secure"] = True
    else:
         return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "component": "celery", "detail": "Insecure serialization configured."}
        )

    return response_data
