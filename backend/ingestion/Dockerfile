# CoreGraph Ingestion Phalanx (Task 010)
FROM python:3.11-slim-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./backend /app/backend
COPY ./Makefile /app/Makefile
ENV PYTHONPATH="/app/backend/ingestion/hooks:/app"
CMD ["python", "-u", "backend/ingestion/hooks/core_ingest.py"]
