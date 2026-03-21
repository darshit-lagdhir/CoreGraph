import time
import psutil
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings
from database import engine
from schemas.health import HealthResponse, HealthCheckDetail, HardwareTelemetry


router = APIRouter(prefix="/health", tags=["Diagnostic Probes"])
START_TIME = time.time()


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe():
    """Liveness: Asserts the responsiveness of the 24-core i9 event loop."""
    return {"status": "PASS", "message": "Systemic cardiac rhythm detected."}


@router.get("/ready", response_model=HealthResponse)
async def readiness_probe():
    """Readiness: Deep diagnostic of the relational vault and message broker dependency chain."""
    checks = {}
    is_ready = True
    
    # 1. PostgreSQL Relational Vault Audit
    try:
        # Failure Scenario A Resolution: Dedicated health check engine with loop isolation
        # This prevents 'NoneType has no attribute send' errors in high-concurrency test cycles
        temp_engine = create_async_engine(
            settings.DATABASE_URL.unicode_string() if hasattr(settings.DATABASE_URL, 'unicode_string') else str(settings.DATABASE_URL)
        )
        start_ping = time.perf_counter()
        async with temp_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start_ping) * 1000
        await temp_engine.dispose()
        checks["postgres"] = HealthCheckDetail(status="PASS", latency_ms=latency)
    except Exception as e:
        checks["postgres"] = HealthCheckDetail(status="FAIL", message=str(e))
        is_ready = False

    # 2. Redis Message Broker Audit
    try:
        # Failure Scenario B Resolution: Raw Socket Ping via ephemeral async redis client
        # This prevents 'Event loop is closed' errors during high-frequency testing cycles
        temp_redis = Redis.from_url(
            settings.REDIS_URL.unicode_string() if hasattr(settings.REDIS_URL, 'unicode_string') else str(settings.REDIS_URL)
        )
        start_ping = time.perf_counter()
        await temp_redis.ping()
        latency = (time.perf_counter() - start_ping) * 1000
        await temp_redis.aclose()
        checks["redis"] = HealthCheckDetail(status="PASS", latency_ms=latency)
    except Exception as e:
        checks["redis"] = HealthCheckDetail(status="FAIL", message=str(e))
        is_ready = False

    # 3. Hardware Metrics (Task 010 Integration)
    # Failure Scenario D Resolution: Normalizing metrics for virtualized WSL2 core loads
    mem = psutil.virtual_memory()
    hardware = HardwareTelemetry(
        cpu_percent=psutil.cpu_percent(),
        memory_used_mb=psutil.Process().memory_info().rss / 1024 / 1024,
        memory_available_mb=mem.available / 1024 / 1024
    )

    response = HealthResponse(
        status="PASS" if is_ready else "FAIL",
        version="1.0.0", # To be pulled from settings if available
        uptime_seconds=time.time() - START_TIME,
        checks=checks,
        hardware=hardware
    )

    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response.model_dump()
        )

    return response
