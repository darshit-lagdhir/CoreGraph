# Foundation-Release-1.0 : Immutable Hardware-Optimized Baseline (Module 1 SEALED)
# Stage 1: Compilation Architecture
FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime Execution Boundary
FROM python:3.13-slim

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 10001 coregraph && \
    useradd -u 10001 -g coregraph -s /bin/bash -m coregraph

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

RUN chown -R coregraph:coregraph /app

USER coregraph

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
