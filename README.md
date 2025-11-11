# AI-News-Summarizer

This repository contains a small multi-service demo that collects news, summarizes articles with a local LLM, and performs sentiment analysis.

Quick steps
1. Install dependencies for local test runs: `pip install -r requirements.txt` (recommended inside a virtualenv).
2. Start services with Docker Compose: `docker compose build` then `docker compose up`.

Ports (default docker-compose mappings)
- Collector service: http://localhost:5001 (container port 5000)
- Summarizer service: http://localhost:5002 (container port 5000)
- Sentiment service: http://localhost:5003 (container port 5000)

Coordinator
You can run a simple coordinator locally to execute the pipeline end-to-end (collect -> summarize -> analyze):

```powershell
python coordinator.py --topic ai
```

Notes about the local LLM
- The summarizer posts to a local LLM endpoint by default at `http://localhost:8000/generate` (see `summarizer/app.py` variable `LOCAL_LLM_API_URL`).
- If you run the services in Docker, containers' `localhost` is the container itself. On Docker Desktop (Windows/macOS) you can set the env `LOCAL_LLM_API_URL` to `http://host.docker.internal:8000/generate` so the summarizer container can reach a LLM running on the host.

Testing
- Run unit tests locally with `pytest`.
