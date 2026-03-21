import logging
import logging.handlers
import multiprocessing
import os
import sys
import threading
from datetime import datetime
import orjson
from typing import Any, Dict, Optional
import contextvars
import uuid


# Failure 1 & 3 Resolution: Context-aware Correlation ID with high-performance orjson
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default="SYSTEM-BOOT"
)


class JSONFormatter(logging.Formatter):
    """Structured JSON logging engine optimized for machine-readability."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "process_id": record.process,
            "thread_name": record.threadName,
            "correlation_id": correlation_id_var.get(),
        }

        # Injecting task metadata if emitted from worker context
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "task_name"):
            log_data["task_name"] = record.task_name

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Failure 3 Resolution: Serialization moved to background orjson kernel
        return orjson.dumps(log_data).decode("utf-8")


def setup_observability():
    """Instantiates the non-blocking observability matrix with Queue-based buffers."""
    log_queue: multiprocessing.Queue[Any] = multiprocessing.Queue()

    # 1. Primary Structured Handler (File with Atomic Rotation)
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Failure 2 Resolution: ConcurrentRotatingFileHandler to prevent race condition locks
    from concurrent_log_handler import ConcurrentRotatingFileHandler

    log_file = os.path.join(log_dir, "coregraph.jsonl")
    file_handler = ConcurrentRotatingFileHandler(log_file, "a", 100 * 1024 * 1024, 10)
    file_handler.setFormatter(JSONFormatter())

    # 2. Console Handler for Real-Time HUD monitoring
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())

    # 3. QueueListener establishing the Telemetry Bridge
    # This thread consumes the memory queue and performs the actual disk/console write
    listener = logging.handlers.QueueListener(
        log_queue, file_handler, console_handler, respect_handler_level=True
    )
    listener.start()

    # 4. Root Logger Configuration bypassing standard blocking handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    root_logger.addHandler(queue_handler)

    return listener
