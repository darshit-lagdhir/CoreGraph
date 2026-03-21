import os
from kombu import Queue
from celery import Celery
from config import settings
import redis

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
