import time
from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from routers.api import api_router
from routers.websocket import websocket_router
from sqlalchemy import text
from redis.asyncio import Redis

from core.config import settings
from database import engine
from worker import celery_app
from core.logging_config import setup_observability
from middleware.trace_middleware import TraceMiddleware


# Non-blocking distributed telemetry initialization
setup_observability()

app = FastAPI(title="CoreGraph API Engine")

app.add_middleware(TraceMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


@app.middleware("http")
async def limit_payload_size(request: Request, call_next):
    # Strict 10MB payload limit enforcing hypervisor memory boundaries
    if request.headers.get("content-length"):
        if int(request.headers.get("content-length")) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Payload dimension actively threatens memory hypervisor bounds.",
            )
    return await call_next(request)


app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Execute raw system ping against isolated infrastructure."""
    response_data = {
        "status": "healthy",
        "database_latency_ms": 0,
        "redis_latency_ms": 0,
        "celery_serializer_secure": False,
    }

    start_db = time.perf_counter()
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "component": "database", "detail": str(e)},
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
            content={"status": "error", "component": "redis", "detail": str(e)},
        )
    response_data["redis_latency_ms"] = round((time.perf_counter() - start_redis) * 1000, 2)

    if (
        celery_app.conf.task_serializer == "json"
        and celery_app.conf.result_serializer == "json"
        and "json" in celery_app.conf.accept_content
    ):
        response_data["celery_serializer_secure"] = True
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "component": "celery",
                "detail": "Insecure serialization configured.",
            },
        )

    return response_data
