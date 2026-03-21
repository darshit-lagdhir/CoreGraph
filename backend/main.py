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
from routers import health


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


app.include_router(health.router)
