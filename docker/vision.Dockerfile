FROM python:3.11-slim

WORKDIR /app

COPY services/vision.py .
COPY db/ ./db/
COPY requirements.txt .
COPY services/celery_app.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "celery_app", "worker", "--queues", "vision", "--loglevel", "info"]