from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route("/", methods=["GET"]) 
def health():
    return jsonify({"service": "collector", "status": "ok"})

@app.route("/collect", methods=["POST"])
def collect_news():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "technology")
    api_key = os.getenv("NEWS_API_KEY")
    summarizer_url = os.getenv("SUMMARIZER_URL")

    if not api_key:
        sample_news = [
            {"title": f"{topic.title()} Advances in 2025", "description": "Researchers are making rapid progress."},
            {"title": f"New Breakthroughs in {topic}", "description": "Experts see major industry shifts."},
            {"title": f"The Future of {topic} Technology", "description": "Innovations are shaping the next decade."},
        ]
        if summarizer_url:
            try:
                fwd = requests.post(f"{summarizer_url}/summarize", json={"articles": sample_news}, timeout=10)
                fwd.raise_for_status()
                return jsonify(fwd.json())
            except Exception:
                # If forwarding fails, return local data
                return jsonify(sample_news)
        else:
            return jsonify(sample_news)

    url = f"https://newsapi.org/v2/everything?q={topic}&pageSize=5&apiKey={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])
    except Exception:
        # Fallback to empty set if API fails
        articles = []

    news_data = [
        {"title": a.get("title"), "description": a.get("description", "")}
        for a in articles[:5]
        if a.get("title")
    ]
    if summarizer_url:
        try:
            fwd = requests.post(f"{summarizer_url}/summarize", json={"articles": news_data}, timeout=10)
            fwd.raise_for_status()
            return jsonify(fwd.json())
        except Exception:
            return jsonify(news_data)
    else:
        return jsonify(news_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
