FROM python:3.11-slim

# Set environment for the Hugging Face non-root user (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app:/home/user/app/backend

WORKDIR $HOME/app

# Copy and install requirements first for caching
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the project
COPY --chown=user . .

# EXPOSE the mandatory Hugging Face port
EXPOSE 7860

# MANDATORY: Run via absolute path and use the config file
# for standalone server mode (Port 7860 is set in the .toml).
CMD ["/home/user/.local/bin/textual-web", "--config", "textual-web.toml"]
