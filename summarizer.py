from flask import Flask, request, jsonify
import os
import requests


app = Flask(__name__)


@app.route("/summarize", methods=["POST"])
def summarize():
data = request.get_json()
articles = data.get("articles", [])
summaries = []


llm_url = os.getenv("LOCAL_LLM_API_URL", "http://localhost:8000/generate")
for article in articles:
text = article.get("description", "")
payload = {"prompt": f"Summarize this: {text}"}
try:
res = requests.post(llm_url, json=payload)
summary = res.json().get("summary", text[:100])
except:
summary = text[:100] # fallback
summaries.append({"title": article["title"], "summary": summary})


return jsonify(summaries)


if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)