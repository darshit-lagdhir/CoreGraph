# Stage 1: Compilation Architecture
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --target=/app/site-packages -r requirements.txt

# Stage 2: Security Patching Layer & Identity
FROM debian:12-slim AS security-patcher

# Define unprivileged user
RUN groupadd -g 65532 nonroot && \
    useradd -u 65532 -g nonroot -s /sbin/nologin nonroot

# Download patched libssl (simulated fix for CRITICAL CVE)
RUN apt-get update && apt-get download libssl3 && \
    mkdir -p /patched && \
    dpkg-deb -X libssl3*.deb /patched

# Prepare log boundaries (satisfying ownership constraint)
RUN mkdir -p /app/backend/logs /app/backend/run && \
    chown -R nonroot:nonroot /app/backend/logs /app/backend/run

# Stage 3: Runtime Execution Boundary
FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app

# Copy Identity
COPY --from=security-patcher /etc/passwd /etc/passwd
COPY --from=security-patcher /etc/group /etc/group

# Patched Binaries
COPY --from=security-patcher /patched/usr/lib/ /usr/lib/

# Copy Dependencies
COPY --from=builder /app/site-packages /app/site-packages
ENV PYTHONPATH=/app/site-packages:/app

# Copy Project Code
COPY --chown=65532:65532 backend/ /app/backend/
COPY --chown=65532:65532 Makefile /app/Makefile
COPY --from=security-patcher --chown=65532:65532 /app/backend/logs /app/backend/logs
COPY --from=security-patcher --chown=65532:65532 /app/backend/run /app/backend/run

# Enforce Unprivileged User
USER 65532

CMD ["/app/site-packages/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
