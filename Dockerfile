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

# MANDATORY: Run via absolute path to bypass PATH issues
# and use the config file to force standalone mode.
CMD ["/home/user/.local/bin/textual-web", "--config", "textual-web.toml", "--port", "7860", "--host", "0.0.0.0"]
