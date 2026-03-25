# S.U.S.E. Simulation Server (Task 010)
FROM python:3.11-slim-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./tooling/simulation_server /app/tooling/simulation_server
COPY ./Makefile /app/Makefile
EXPOSE 8081
ENV PYTHONPATH="/app/tooling/simulation_server:/app"
CMD ["uvicorn", "tooling.simulation_server.main:app", "--host", "0.0.0.0", "--port", "8081"]
