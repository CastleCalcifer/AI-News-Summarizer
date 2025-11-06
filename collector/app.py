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
    enable_get = (os.getenv("ENABLE_GET_TEST_ROUTES", "0").lower() in {"1", "true", "yes"})

    if not api_key:
        sample_news = [
            {"title": f"{topic.title()} Advances in 2025", "description": "Researchers are making rapid progress.", "source_url": "https://example.com/mock1"},
            {"title": f"New Breakthroughs in {topic}", "description": "Experts see major industry shifts.", "source_url": "https://example.com/mock2"},
            {"title": f"The Future of {topic} Technology", "description": "Innovations are shaping the next decade.", "source_url": "https://example.com/mock3"},
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
        {"title": a.get("title"), "description": a.get("description", ""), "source_url": a.get("url")}
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

# Optional GET route for browser-based testing
@app.route("/collect", methods=["GET"])
def collect_news_get():
    if not (os.getenv("ENABLE_GET_TEST_ROUTES", "0").lower() in {"1", "true", "yes"}):
        return jsonify({"error": "GET testing routes disabled"}), 404
    topic = request.args.get("topic", "technology")
    # Re-use POST logic via internal call
    return collect_news.__wrapped__() if hasattr(collect_news, "__wrapped__") else collect_news()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
