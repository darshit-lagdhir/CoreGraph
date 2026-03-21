#!/bin/bash
set -e

echo "[CI Bootstrap] Initializing Surgical Wait-for-IT logic..."

# High-velocity pg_isready poll (100ms)
MAX_ATTEMPTS=50
ATTEMPT=0

# Wait for PostgreSQL
until PGPASSWORD=password123 pg_isready -h 127.0.0.1 -p 5433 -U admin > /dev/null 2>&1; do
  ATTEMPT=$((ATTEMPT+1))
  if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "CRITICAL FAILURE: PostgreSQL deadlock."
    exit 1
  fi
  sleep 0.1
done

echo "[CI Bootstrap] Relational Vault healthy. Allocating memory boundaries..."
# Tuning configurations for CI constraint
export WORKER_MAX_CONCURRENCY=8
export POSTGRES_SHARED_BUFFERS="512MB"

echo "[CI Bootstrap] Environments tuned. Ready for matrix testing."
exit 0
