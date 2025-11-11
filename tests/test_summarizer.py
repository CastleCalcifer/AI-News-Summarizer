from unittest.mock import patch
from summarizer.app import app


def test_summarize_no_articles():
    client = app.test_client()
    resp = client.post("/summarize", json={"articles": []})
    assert resp.status_code == 200
    assert resp.get_json() == []


@patch("summarizer.app.requests.post")
def test_summarize_and_forward_to_sentiment(mock_post, monkeypatch):
    # First call: LLM summary
    class MockResp:
        def __init__(self, payload):
            self._payload = payload
        def json(self):
            return self._payload
        def raise_for_status(self):
            return None
    
    mock_post.side_effect = [
        MockResp({"summary": "Short summary 1"}),  # LLM response for article 1
        MockResp({"summary": "Short summary 2"}),  # LLM response for article 2
        MockResp({  # Sentiment service response
            "analysis": [{"title": "t1", "polarity": 0.2}],
            "overall_tone": "positive",
            "average_polarity": 0.2,
        }),
    ]

    monkeypatch.setenv("SENTIMENT_URL", "http://sentiment:5000")

    client = app.test_client()
    resp = client.post(
        "/summarize",
        json={
            "articles": [
                {"title": "t1", "description": "desc1"},
                {"title": "t2", "description": "desc2"},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("overall_tone") in {"positive", "neutral", "negative"}
