from sentiment.app import app


def test_analyze_empty():
    client = app.test_client()
    resp = client.post("/analyze", json={"summaries": []})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["overall_tone"] == "neutral"
    assert data["average_polarity"] == 0.0


def test_analyze_positive_text():
    client = app.test_client()
    summaries = [{"title": "t1", "summary": "This is great and wonderful."}]
    resp = client.post("/analyze", json={"summaries": summaries})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["overall_tone"] in {"positive", "neutral", "negative"}
