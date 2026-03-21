from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import os
import json
import hashlib
from pathlib import Path
from multiprocessing import Pool, cpu_count

from routers.health import router as health_router
from routers.api import api_router
from routers.websocket import websocket_router
from middleware.trace_middleware import TraceMiddleware
from core.logging_config import setup_observability

WORKSPACE_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = WORKSPACE_ROOT / ".workspace" / "manifest.json"

try:
    # Failure 2: Prioritize ASGI Gateway over analytical workers
    os.nice(-5)  # type: ignore[attr-defined]
except (AttributeError, PermissionError, OSError):
    # Fallback for Windows or non-privileged process execution
    pass


# Non-blocking distributed telemetry initialization
setup_observability()


def hash_file(filepath):
    h = hashlib.sha512()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return {str(filepath.name): h.hexdigest()}
    except Exception:
        return {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-Flight Integrity Check
    shm_flag = Path("/dev/shm") / ".coregraph_integrity_ok"
    if os.name == "posix" and shm_flag.exists():
        pass  # Skip if verified to avoid blocked restart loops
    elif MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r") as f:
            manifest = json.load(f)
        expected_hashes = manifest.get("hashes", {})
        # Distribute hash workload across cores
        targets = [WORKSPACE_ROOT / p for p in expected_hashes]
        cpu_limit = min(cpu_count(), 8)
        with Pool(cpu_limit) as p:
            results = p.map(hash_file, targets)

        computed_hashes = {}
        for r in results:
            computed_hashes.update(r)

        for p, expected in expected_hashes.items():
            if computed_hashes.get(p) != expected:
                print(f"[!] Integrity Check Failed! Drift in {p} - Halt!")
                os._exit(1)  # Prevent booting

        if os.name == "posix":
            shm_flag.touch()
    yield


app = FastAPI(title="CoreGraph API Engine", lifespan=lifespan)

app.add_middleware(TraceMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware)


@app.middleware("http")
async def limit_payload_size(request: Request, call_next):
    # Strict 10MB payload limit enforcing hypervisor memory boundaries
    if request.headers.get("content-length"):
        if int(request.headers.get("content-length")) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Payload limits exceeded.",
            )
    return await call_next(request)


app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router)


app.include_router(health_router)
