from flask import Flask, request, jsonify
import os
import requests
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/", methods=["GET"]) 
def health():
    return jsonify({"service": "summarizer", "status": "ok"})

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json(silent=True) or {}
    articles = data.get("articles", [])
    summaries = []
    
    
    # Default to Ollama's host port if running locally on 11434
    llm_url = os.getenv("LOCAL_LLM_API_URL", "http://localhost:11434/api/generate")
    llm_model = os.getenv("LOCAL_LLM_MODEL")
    include_llm_output = (os.getenv("INCLUDE_LLM_OUTPUT", "1").lower() in {"1", "true", "yes"})
    sentiment_url = os.getenv("SENTIMENT_URL")
    for article in articles:
        text = article.get("description", "")
        # Build flexible payload; include model if provided (useful for Ollama)
        if llm_model:
            payload = {"model": llm_model, "prompt": f"Summarize this: {text}"}
        else:
            payload = {"prompt": f"Summarize this: {text}"}
        try:
            # Debug log: show method, URL and a truncated payload so we can diagnose 405/404 issues
            try:
                print(f"LLM POST -> {llm_url} payload={str(payload)[:400]}")
            except Exception:
                pass
            res = requests.post(llm_url, json=payload, timeout=10)
            try:
                data = res.json()
            except Exception:
                data = None

            # If the LLM returned an HTTP error (e.g., 405 Method Not Allowed), capture that
            if getattr(res, "status_code", 200) >= 400:
                llm_output = {"status": res.status_code, "body": (res.text or "")}
                # don't try to parse a summary from an error response
                summary = None
            else:
                summary = None
                if isinstance(data, dict):
                    summary = data.get("summary") or data.get("result")
                    if not summary:
                        choices = data.get("choices")
                        if isinstance(choices, list) and choices:
                            first = choices[0]
                            summary = first.get("text") or (first.get("message", {}).get("content") if isinstance(first.get("message"), dict) else None)
                    if not summary and "output" in data:
                        out = data.get("output")
                        if isinstance(out, str):
                            summary = out
                        elif isinstance(out, list) and out:
                            summary = " ".join([str(x) for x in out])
                if not summary:
                    text_body = res.text or ""
                    summary = text_body.strip() or text[:100]
                # capture a safe representation of the LLM output
                try:
                    llm_output = data if isinstance(data, (dict, list)) else (res.text or None)
                except Exception:
                    llm_output = (res.text or None)
        except Exception:
            summary = text[:100] # fallback
            llm_output = None
        summaries.append({
            "title": article["title"],
            "summary": summary,
            "source_url": article.get("source_url")
        })
        # Optionally attach raw LLM output to the last appended summary
        if include_llm_output:
            try:
                if llm_output is not None:
                    summaries[-1]["llm_output"] = llm_output
            except Exception:
                pass
        
    # Return the summaries without auto-forwarding to sentiment
    # The UI dashboard will handle calling sentiment separately
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
    llm_url = os.getenv("LOCAL_LLM_API_URL", "http://localhost:11434/api/generate")
    llm_model = os.getenv("LOCAL_LLM_MODEL")
    sentiment_url = os.getenv("SENTIMENT_URL")
    if llm_model:
        payload = {"model": llm_model, "prompt": f"Summarize this: {description}"}
    else:
        payload = {"prompt": f"Summarize this: {description}"}
    try:
        # Debug log: show method, URL and a truncated payload so we can diagnose 405/404 issues
        try:
            print(f"LLM POST -> {llm_url} payload={str(payload)[:400]}")
        except Exception:
            pass
        res = requests.post(llm_url, json=payload, timeout=10)
        try:
            data = res.json()
        except Exception:
            data = None
        summary = None
        if isinstance(data, dict):
            summary = data.get("summary") or data.get("result")
            if not summary:
                choices = data.get("choices")
                if isinstance(choices, list) and choices:
                    first = choices[0]
                    summary = first.get("text") or (first.get("message", {}).get("content") if isinstance(first.get("message"), dict) else None)
            if not summary and "output" in data:
                out = data.get("output")
                if isinstance(out, str):
                    summary = out
                elif isinstance(out, list) and out:
                    summary = " ".join([str(x) for x in out])
        if not summary:
            summary = (res.text or "").strip() or description[:100]
    except Exception:
        summary = description[:100]
    summaries = [{"title": title, "summary": summary, "source_url": source_url}]
    # Return summaries without auto-forwarding to sentiment
    return jsonify(summaries)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)