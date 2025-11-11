# AI-News-Summarizer

This repository contains a small multi-service demo that collects news, summarizes articles with a local LLM, and performs sentiment analysis.

Quick start with Web UI (recommended)
1. Ensure Ollama is running on your host at port 11434 with a model like `ollama pull llama2`.
2. Start all services with Docker Compose:
   ```powershell
   docker compose build
   docker compose up
   ```
   # Run the UI dashboard on your host
python ui_dashboard.py
3. Open the interactive UI in your browser:
   - **http://localhost:5000** ← Click buttons to test each step!

Services & Ports
- **UI Dashboard**: http://localhost:5000 (web interface to test pipeline)
- **Collector service**: http://localhost:5001 (collect news articles)
- **Summarizer service**: http://localhost:5002 (LLM summaries)
- **Sentiment service**: http://localhost:5003 (sentiment analysis & web UI)

Web UI Features
- Click "Collect Articles" to fetch news for a topic
- Click "Summarize Articles" to run LLM summaries
- Click "Analyze Sentiment" to compute sentiment scores
- Click "Run Full Pipeline" to execute all steps end-to-end
- See live JSON responses in the UI

Command-line Testing
If you prefer the CLI, use the coordinator script:
```powershell
python coordinator.py --topic ai
```

Notes about Ollama
- The summarizer connects to Ollama at `http://localhost:11434/api/generate` (local runs) or `http://host.docker.internal:11434/api/generate` (Docker).
- If running Ollama on a different host/port, set `LOCAL_LLM_API_URL` env var:
  - Docker: add to `summarizer` environment in `docker-compose.yml`
  - Local: `$env:LOCAL_LLM_API_URL='http://localhost:<port>/api/generate'` before running `python summarizer/app.py`
- Optionally set `LOCAL_LLM_MODEL` to select a specific model (e.g., `llama2`, `neural-chat`).

Testing
- Run unit tests locally with `pytest`.
