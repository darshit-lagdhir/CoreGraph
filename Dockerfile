# COREGRAPH MASTER ENGINEERING SPECIFICATION: CLOUD PHALANX
# HUGGING FACE SPACE DEPLOYMENT (PORT 7860, NON-ROOT, TEXTUAL-WEB WEBSOCKET TUNNEL)

FROM python:3.11-slim

# Enforce 150MB RSS Mandate & Cloud Security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MALLOC_ARENA_MAX=2 \
    PYTHONPATH=/app:/app/backend

# Create non-root user (UID 1000) for Hugging Face security compliance
RUN useradd -m -u 1000 coregraph_user

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Layer Caching: Requirements
COPY requirements.txt .
# Ensure textual-web is installed for the websocket bridge
RUN pip install --no-cache-dir -r requirements.txt textual-web

# Copy the Backend Core and Terminal HUD
COPY backend/ ./backend/

# Physical Permissions Handshake
RUN chown -R 1000:1000 /app

# Switch to Sovereign User
USER 1000

# Cloud Ingress Port
EXPOSE 7860

# Terminal End-to-End Handshake
# Tunneling the 144Hz HUD via Textual-Web on 0.0.0.0:7860
CMD ["textual", "serve", "--port", "7860", "--host", "0.0.0.0", "python", "backend/terminal_hud.py"]
