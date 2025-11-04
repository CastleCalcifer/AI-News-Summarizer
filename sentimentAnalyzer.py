from flask import Flask, request, jsonify
from textblob import TextBlob


app = Flask(__name__)


@app.route("/analyze", methods=["POST"])
def analyze():
data = request.get_json()
summaries = data.get("summaries", [])


sentiments = []
total_polarity = 0
for item in summaries:
text = item.get("summary", "")
polarity = TextBlob(text).sentiment.polarity
sentiments.append({"title": item["title"], "polarity": polarity})
total_polarity += polarity


avg_polarity = total_polarity / len(sentiments) if sentiments else 0
mood = "positive" if avg_polarity > 0.1 else "negative" if avg_polarity < -0.1 else "neutral"


return jsonify({"analysis": sentiments, "overall_tone": mood})


if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)