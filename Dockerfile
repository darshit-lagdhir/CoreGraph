# COREGRAPH SOVEREIGN DOCKERFILE - APPROACH B (TTYD)
FROM python:3.11-slim

# Switch to root to install the system-level bridge
USER root
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64 -o /usr/bin/ttyd \
    && chmod +x /usr/bin/ttyd \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the Sovereign User (Hugging Face UID 1000)
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Copy and install Python sinew
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the Hadronic Core
COPY --chown=user . .

# Ensure the user owns the workspace
RUN chown -R user:user /home/user/app
USER user

# Set environment for terminal radiance
ENV PATH="/home/user/.local/bin:${PATH}" \
    PYTHONPATH="/home/user/app:/home/user/app/backend" \
    TERM=xterm-256color

# EXPOSE the mandatory Cloud Phalanx port
EXPOSE 7860

# THE ZENITH HANDSHAKE:
# ttyd -p [port] -i [interface] [command]
# This serves your backend directly to the web with NO config files required.
# Note: Using terminal_hud.py as it is our supreme TUI entry point.
CMD ["ttyd", "-p", "7860", "-i", "0.0.0.0", "python", "backend/terminal_hud.py"]
