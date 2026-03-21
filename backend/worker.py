import redis
from celery import Celery
from kombu import Queue
from celery.signals import task_prerun, task_postrun, before_task_publish
from core.config import settings
from core.logging_config import setup_observability, correlation_id_var
import logging

# Initialize structured observability matrix for high-concurrency trace captures
setup_observability()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "coregraph_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
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
    worker_max_tasks_per_child=100,
    worker_max_memory_per_child=512000,
    result_expires=3600,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)


class CoreGraphTask(celery_app.Task):
    abstract = True

    def on_success(self, retval, task_id, args, kwargs):
        try:
            client = redis.from_url(settings.REDIS_URL)
            client.hset(f"coregraph:progress:{task_id}", "status", "SUCCESS")
            client.close()
        except redis.ConnectionError:
            pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            client = redis.from_url(settings.REDIS_URL)
            client.hset(f"coregraph:progress:{task_id}", "status", "FAILURE")
            client.close()
        except redis.ConnectionError:
            pass


@before_task_publish.connect
def before_publish_handler(headers, **kwargs):
    """Broker Injection: Piggybacks the current correlation ID onto the outgoing task matrix."""
    headers["correlation_id"] = correlation_id_var.get()


@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Context Initialization: Retrieves the correlation ID from the task headers in the worker context."""
    corr_id = getattr(task.request, "correlation_id", "STRAY-TASK")
    # Store token for later reset
    task._correlation_token = correlation_id_var.set(corr_id)
    logging.info(f"Task {task.name}[{task_id}] starting with correlation {corr_id}")


@task_postrun.connect
def task_postrun_handler(task, *args, **kwargs):
    """Cleanup: Flushes the worker-local context variable to prevent cross-task trace contamination."""
    if hasattr(task, "_correlation_token"):
        correlation_id_var.reset(task._correlation_token)
