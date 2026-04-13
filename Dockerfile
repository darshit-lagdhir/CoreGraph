# MULTI-STAGE ZERO-CC DEPLOYMENT KERNEL
# STAGE 1: COMPILATION MANIFOLD
FROM python:3.11-slim as builder
WORKDIR /build
COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# STAGE 2: RUNTIME ENCAPSULATION MANIFOLD
FROM python:3.11-slim as runtime
WORKDIR /app

# STRICT INFRASTRUCTURE-GATING AUDIT
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONASYNCIODEBUG=0 \
    WORKER_CONCURRENCY=1 \
    COREGRAPH_HEADLESS_MODE=1

# ASYNCHRONOUS MECHANICAL SHIELD
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# IN-PLACE ARCHITECTURAL MECHANICAL SEAL
COPY backend/ ./backend/

# ZERO-CC CONTAINER GATEWAY IGNITION
EXPOSE 8000
CMD ["python", "backend/main.py"]

