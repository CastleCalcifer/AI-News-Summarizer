"""Simple coordinator to run the pipeline locally:
  POST -> /collect (localhost:5001)
  POST -> /summarize (localhost:5002) if needed
  POST -> /analyze (localhost:5003)

Usage:
  python coordinator.py --topic ai
"""
import requests
import argparse
import sys
import json


def post(url, payload, timeout=10):
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"ERROR POST {url}: {e}")
        return None


def run_pipeline(topic, collector_url, summarizer_url, sentiment_url):
    print(f"1) Collecting news for topic: {topic}")
    collected = post(f"{collector_url}/collect", {"topic": topic})
    if collected is None:
        print("Collect step failed. Exiting.")
        return 1

    # If collector already forwarded to summarizer it may return summaries (have 'summary')
    if isinstance(collected, dict) and collected.get("overall_tone"):
        # Collector forwarded all the way through
        print("Collector already returned final analysis:")
        print(json.dumps(collected, indent=2))
        return 0

    if isinstance(collected, list) and collected and isinstance(collected[0], dict) and "summary" in collected[0]:
        summaries = collected
        print("Collector returned summaries; skipping summarizer step.")
    else:
        print("2) Summarizing articles")
        summaries = post(f"{summarizer_url}/summarize", {"articles": collected})
        if summaries is None:
            print("Summarize step failed. Exiting.")
            return 1

    # If summarizer forwarded to sentiment it may return final analysis
    if isinstance(summaries, dict) and summaries.get("overall_tone"):
        print("Summarizer already returned final analysis:")
        print(json.dumps(summaries, indent=2))
        return 0

    print("3) Analyzing sentiment")
    analysis = post(f"{sentiment_url}/analyze", {"summaries": summaries})
    if analysis is None:
        print("Analyze step failed. Exiting.")
        return 1

    print("Final analysis:")
    print(json.dumps(analysis, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--topic", default="ai", help="Topic to collect")
    p.add_argument("--collector", default="http://localhost:5001", help="Collector base URL")
    p.add_argument("--summarizer", default="http://localhost:5002", help="Summarizer base URL")
    p.add_argument("--sentiment", default="http://localhost:5003", help="Sentiment base URL")
    args = p.parse_args()

    sys.exit(run_pipeline(args.topic, args.collector, args.summarizer, args.sentiment))


if __name__ == "__main__":
    main()
