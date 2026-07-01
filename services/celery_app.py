from celery import Celery
import logging

logging.basicConfig(level=logging.INFO)

app = Celery(
    "screenshot_pipeline",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["services.vision", "services.embedding", "services.grouping"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

app.conf.task_routes = {
    "vision.process": {"queue": "vision"},
    "embedding.process": {"queue": "embedding"},
    "grouping.process": {"queue": "grouping"},
}
