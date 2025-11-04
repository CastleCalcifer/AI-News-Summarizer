# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime deps
RUN pip install --no-cache-dir flask requests

# Copy application code (compose will set context to repo root)
COPY news_collector/app.py /app/app.py

EXPOSE 5000

CMD ["python", "/app/app.py"]


