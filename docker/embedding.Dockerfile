FROM python 3.11-slim

WORKDIR /app

COPY services/embedding.py .
COPY db/ ./db/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "embedding.py"]