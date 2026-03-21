import redis
from typing import Any

from celery import Celery
from kombu import Queue
from celery.signals import task_prerun, task_postrun, before_task_publish
from core.config import settings
from core.logging_config import setup_observability, correlation_id_var
import logging

# Initialize structured observability matrix for high-concurrency trace captures
setup_observability()  # type: ignore
logger = logging.getLogger(__name__)

celery_app = Celery(
    "coregraph_worker",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_queues=(
        Queue("default"),
        Queue("ingestion"),
        Queue("analytics"),
    ),
    task_default_queue="default",
    task_routes={
        "tasks.ingestion.*": {"queue": "ingestion"},
        "tasks.computation.*": {"queue": "analytics"},
    },
    worker_concurrency=16,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    worker_max_memory_per_child=512000,
    result_expires=3600,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)


class CoreGraphTask(celery_app.Task):  # type: ignore
    abstract = True

    def on_success(self, retval: Any, task_id: str, args: Any, kwargs: Any) -> None:
        try:
            client = redis.from_url(str(settings.REDIS_URL))
            client.hset(f"coregraph:progress:{task_id}", "status", "SUCCESS")
            client.close()
        except redis.ConnectionError:
            pass

    def on_failure(self, exc: Any, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        try:
            client = redis.from_url(str(settings.REDIS_URL))
            client.hset(f"coregraph:progress:{task_id}", "status", "FAILURE")
            client.close()
        except redis.ConnectionError:
            pass


@before_task_publish.connect  # type: ignore
def before_publish_handler(headers: Any, **kwargs: Any) -> None:
    """Broker Injection: Piggybacks the current correlation ID onto the outgoing task matrix."""
    headers["correlation_id"] = correlation_id_var.get()


@task_prerun.connect  # type: ignore
def task_prerun_handler(task_id: str, task: Any, *args: Any, **kwargs: Any) -> None:
    """
    Context Initialization: Retrieves the correlation ID from the task headers
    in the worker context.
    """
    corr_id = getattr(task.request, "correlation_id", "STRAY-TASK")
    # Store token for later reset
    task._correlation_token = correlation_id_var.set(corr_id)
    logging.info(f"Task {task.name}[{task_id}] starting with correlation {corr_id}")


@task_postrun.connect  # type: ignore
def task_postrun_handler(task: Any, *args: Any, **kwargs: Any) -> None:
    """
    Cleanup: Flushes the worker-local context variable to prevent cross-task trace
    contamination.
    """
    if hasattr(task, "_correlation_token"):
        correlation_id_var.reset(task._correlation_token)
