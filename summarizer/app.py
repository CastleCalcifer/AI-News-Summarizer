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
        summaries.append({"title": article["title"], "summary": summary})
    
    
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