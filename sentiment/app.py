from flask import Flask, request, jsonify
from textblob import TextBlob
import os
import requests
from markupsafe import escape
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["GET"]) 
def health():
    return jsonify({"service": "sentiment", "status": "ok"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    summaries = data.get("summaries", [])

    sentiments = []
    total_polarity = 0.0
    for item in summaries:
        text = item.get("summary", "") or ""
        polarity = float(TextBlob(text).sentiment.polarity)
        sentiments.append({
            "title": item.get("title"),
            "polarity": polarity,
            "source_url": item.get("source_url")
        })
        total_polarity += polarity

    avg_polarity = (total_polarity / len(sentiments)) if sentiments else 0.0
    mood = "positive" if avg_polarity > 0.1 else "negative" if avg_polarity < -0.1 else "neutral"

    # Extract topic from request if available, otherwise use generic term
    topic = data.get("topic", "this topic")
    
    # Simple, user-friendly message
    sentiment_message = f"News about {topic} is currently: {mood} 📊"

    return jsonify({"message": sentiment_message, "mood": mood, "average_polarity": round(avg_polarity, 2)})


@app.route("/summarizer", methods=["GET"])
def summarizer_page():
    """Render a simple HTML page showing summaries for a topic.
    This endpoint will call the collector and summarizer services internally.
    """
    topic = request.args.get("topic", "technology")
    # Allow overriding service locations via env vars (use service names in compose by default)
    collector_url = os.getenv("COLLECTOR_URL", "http://collector:5000")
    summarizer_url = os.getenv("SUMMARIZER_URL", "http://summarizer:5000")

    # 1) Collect - try service name first, then fall back to localhost mapped port for host runs
    articles = None
    collect_attempts = [collector_url, os.getenv("COLLECTOR_FALLBACK_URL", "http://localhost:5001")]
    for url in collect_attempts:
        try:
            cresp = requests.post(f"{url}/collect", json={"topic": topic}, timeout=10)
            cresp.raise_for_status()
            articles = cresp.json()
            break
        except Exception:
            articles = None
    if articles is None:
        return f"<h1>Error collecting articles</h1><pre>Could not reach collector at {collect_attempts}</pre>", 500

    # 2) Summarize
    # 2) Summarize - try service name first, then fall back to localhost mapped port for host runs
    summaries = None
    summarize_attempts = [summarizer_url, os.getenv("SUMMARIZER_FALLBACK_URL", "http://localhost:5002")]
    for url in summarize_attempts:
        try:
            sresp = requests.post(f"{url}/summarize", json={"articles": articles}, timeout=20)
            sresp.raise_for_status()
            summaries = sresp.json()
            break
        except Exception:
            summaries = None
    if summaries is None:
        return f"<h1>Error summarizing articles</h1><pre>Could not reach summarizer at {summarize_attempts}</pre>", 500

    # Build HTML
    html = ["<html><head><title>Summaries</title></head><body>"]
    html.append(f"<h1>Summaries for {escape(topic)}</h1>")
    if not summaries:
        html.append("<p>No summaries returned.</p>")
    else:
        for item in summaries:
            title = escape(item.get("title", "(no title)"))
            summary = escape(item.get("summary", ""))
            html.append(f"<h2>{title}</h2>")
            html.append(f"<p>{summary}</p>")
            if item.get("source_url"):
                html.append(f"<p>Source: <a href=\"{escape(item.get('source_url'))}\">{escape(item.get('source_url'))}</a></p>")
            # if summarizer included raw llm output, show it truncated
            if item.get("llm_output"):
                llm_text = escape(str(item.get("llm_output")))
                if len(llm_text) > 1000:
                    llm_text = llm_text[:1000] + "..."
                html.append("<h3>LLM raw output</h3>")
                html.append(f"<pre>{llm_text}</pre>")

    html.append("</body></html>")
    return "\n".join(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
