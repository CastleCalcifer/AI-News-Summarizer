from flask import Flask, request, jsonify
import os
import requests


app = Flask(__name__)


@app.route("/", methods=["GET"]) 
def health():
    return jsonify({"service": "summarizer", "status": "ok"})

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json(silent=True) or {}
    articles = data.get("articles", [])
    summaries = []
    
    
    llm_url = os.getenv("LOCAL_LLM_API_URL", "http://localhost:8000/generate")
    sentiment_url = os.getenv("SENTIMENT_URL")
    for article in articles:
        text = article.get("description", "")
        payload = {"prompt": f"Summarize this: {text}"}
        try:
            res = requests.post(llm_url, json=payload)
            summary = res.json().get("summary", text[:100])
        except:
            summary = text[:100] # fallback
        summaries.append({
            "title": article["title"],
            "summary": summary,
            "source_url": article.get("source_url")
        })
    
    
    if sentiment_url:
        try:
            fwd = requests.post(f"{sentiment_url}/analyze", json={"summaries": summaries}, timeout=10)
            fwd.raise_for_status()
            return jsonify(fwd.json())
        except Exception:
            return jsonify(summaries)
    else:
        return jsonify(summaries)

# Optional GET route for browser-based testing
@app.route("/summarize", methods=["GET"]) 
def summarize_get():
    if not (os.getenv("ENABLE_GET_TEST_ROUTES", "0").lower() in {"1", "true", "yes"}):
        return jsonify({"error": "GET testing routes disabled"}), 404
    title = request.args.get("title", "Sample title")
    description = request.args.get("description", "Sample description")
    source_url = request.args.get("source_url")
    # Perform the same summarization logic for a single article
    llm_url = os.getenv("LOCAL_LLM_API_URL", "http://localhost:8000/generate")
    sentiment_url = os.getenv("SENTIMENT_URL")
    payload = {"prompt": f"Summarize this: {description}"}
    try:
        res = requests.post(llm_url, json=payload)
        summary = res.json().get("summary", description[:100])
    except Exception:
        summary = description[:100]
    summaries = [{"title": title, "summary": summary, "source_url": source_url}]
    if sentiment_url:
        try:
            fwd = requests.post(f"{sentiment_url}/analyze", json={"summaries": summaries}, timeout=10)
            fwd.raise_for_status()
            return jsonify(fwd.json())
        except Exception:
            return jsonify(summaries)
    else:
        return jsonify(summaries)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)