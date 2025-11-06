from flask import Flask, request, jsonify
from textblob import TextBlob

app = Flask(__name__)

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

    return jsonify({"analysis": sentiments, "overall_tone": mood, "average_polarity": avg_polarity})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
