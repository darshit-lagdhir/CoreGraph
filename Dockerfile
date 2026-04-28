# COREGRAPH SOVEREIGN DOCKERFILE - APPROACH B (TTYD)
# HEARTBEAT: 2026-04-27T08:24:50Z | GENESIS RE-IGNITION
FROM python:3.11-slim

# Switch to root to install the system-level bridge and dependencies
USER root
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64 -o /usr/bin/ttyd \
    && chmod +x /usr/bin/ttyd \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the Sovereign User for runtime isolation
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Install Python dependencies GLOBALLY as root to avoid PATH/Module issues
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Hadronic Core and establish ownership
COPY . .
RUN chown -R user:user /home/user/app

# Switch to Sovereign User for runtime security
USER user

# Set environment for terminal radiance
ENV PATH="/home/user/.local/bin:${PATH}" \
    PYTHONPATH="/home/user/app:/home/user/app/backend" \
    TERM=xterm-256color \
    PYTHONUNBUFFERED=1

# EXPOSE the mandatory Cloud Phalanx port
EXPOSE 7860

# THE ZENITH HANDSHAKE:
CMD ["ttyd", "-p", "7860", "-i", "0.0.0.0", "python", "backend/terminal_hud.py"]
