from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

@app.route("/collect", methods=["POST"])
def collect_news():
    data = request.get_json()
    topic = data.get("topic", "technology")
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        # Mock data fallback
        print("[Mock Mode] No NEWS_API_KEY found. Using sample data.")
        sample_news = [
            {"title": f"{topic.title()} Advances in 2025", "description": "Researchers are making rapid progress."},
            {"title": f"New Breakthroughs in {topic}", "description": "Experts see major industry shifts."},
            {"title": f"The Future of {topic} Technology", "description": "Innovations are shaping the next decade."},
        ]
        return jsonify(sample_news)

    # Real API call
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json().get("articles", [])
    news_data = [{"title": a["title"], "description": a["description"]} for a in articles[:5]]
    return jsonify(news_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)