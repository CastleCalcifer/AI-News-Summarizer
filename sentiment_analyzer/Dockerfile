# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir flask textblob && \
    python -m textblob.download_corpora

COPY sentimentAnalyzer.py /app/sentimentAnalyzer.py

EXPOSE 5000

CMD ["python", "/app/sentimentAnalyzer.py"]


