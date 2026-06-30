FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY services/ ./services/
COPY db/ ./db/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "services.celery_app", "worker", "--queues", "grouping", "--loglevel", "info", "--concurrency", "1"]