# Distilled CoreGraph Forensic Kernel - Headless Mode (Module 15 / April 20th Seal)
FROM python:3.13-alpine AS builder

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    && rm -rf /var/cache/apk/*

WORKDIR /app
COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Absolute Hardware Sovereignty Boundary
FROM python:3.13-alpine

RUN apk add --no-cache libpq && rm -rf /var/cache/apk/*

RUN addgroup -g 10001 coregraph && \
    adduser -u 10001 -G coregraph -s /bin/sh -D coregraph

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

RUN chown -R coregraph:coregraph /app

USER coregraph

CMD ["uvicorn", "main:invoke_orchestration", "--host", "0.0.0.0", "--port", "8000"]

