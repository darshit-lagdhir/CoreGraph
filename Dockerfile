# Module 4 - Task 023: REDLINE-Optimized Production Container
# Base utilization of Slim-Debian for Python execution to minimize image footprint.

FROM python:3.13-slim-bullseye AS builder

WORKDIR /coregraph

# Silicon-Native dependencies for PostgreSQL async I/O drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- PRODUCTION STAGE ---
FROM python:3.13-slim-bullseye

# Environment constraints preventing memory leak swap conditions
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MALLOC_ARENA_MAX=2 \
    PYTHONASYNCIODEBUG=0

WORKDIR /coregraph

# Pull native drivers from builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

# Establish system PATH
ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Launch into the Host Sensing Kernel before initiating the Ingestion Phalanx
ENTRYPOINT ["python", "-c", "import sys; from backend.ingestion.sensing import HostSensingKernel; HostSensingKernel().generate_master_constants(); from backend.ingestion.phalanx import UnifiedIngestionPhalanx; sys.exit(0)"]
