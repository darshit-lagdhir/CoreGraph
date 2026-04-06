# COREGRAPH MASTER ENGINEERING SPECIFICATION: MODULE 15 - TASK 09
# MULTI-ARCHITECTURE BUILD VALIDATION: UNIVERSAL SILICON SEAL

# --- STAGE 1: FRONTEND BUILD (VITE/WEBGL COMPILATION) ---
FROM --platform=$BUILDPLATFORM node:20-slim AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --quiet
COPY . .
RUN npm run build

# --- STAGE 2: BACKEND BUILD (ARCH-SENSITIVE COMPILATION) ---
FROM --platform=$BUILDPLATFORM python:3.11-slim-bullseye AS backend-builder
ARG TARGETPLATFORM
WORKDIR /app

# Installing Toolchains for Native Silicon Optimization
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-aarch64-linux-gnu \
    gcc-x86-64-linux-gnu \
    libpq-dev \
    binutils \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/ingestion/requirements.txt .

# Multi-Platform Binary Optimization: Installing Architecture-Native Wheels
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        export CC=aarch64-linux-gnu-gcc; \
    fi && \
    pip install --user --no-cache-dir -r requirements.txt

# Binary Stripping: Eradicating non-essential debug symbols for 150MB Mandate
RUN find /root/.local -name "*.so" -exec strip --strip-debug {} +

# --- STAGE 3: PRODUCTION SOVEREIGN VESSEL (DISTROLESS) ---
FROM gcr.io/distroless/python3-debian11
WORKDIR /coregraph

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MALLOC_ARENA_MAX=2 \
    PYTHONPATH=/coregraph:/coregraph/backend

# Copy site-packages from builder
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy minified frontend assets
COPY --from=frontend-builder /app/dist ./frontend/dist

# Copy the Backend Core (Root context bridge)
COPY backend/ ./backend/
COPY master_orchestrator.py .

ENTRYPOINT ["python", "master_orchestrator.py"]
