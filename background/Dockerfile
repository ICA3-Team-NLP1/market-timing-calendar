FROM python:3.11-slim AS celery-worker
WORKDIR /app
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY background/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["celery", "-A", "background.celery_app", "worker", "--loglevel=info"]