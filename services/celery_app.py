from celery import Celery

app = Celery(
    'screenshot_pipeline',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

app.conf.update(
    task_serializer='json',
    accpet_serializer=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

app.conf.task_routes = {
    'vision.process': {'queue': 'vision'},
    'embedding.process': {'queue': 'embedding'},
    'grouping.process' : {'queue': 'grouping'},
}