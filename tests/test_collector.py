import os
import json
from unittest.mock import patch
from collector.app import app


def test_collect_mock_data_no_api_key(monkeypatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    client = app.test_client()

    resp = client.post("/collect", json={"topic": "ai"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all("title" in x and "description" in x for x in data)


@patch("collector.app.requests.get")
def test_collect_with_api_key_and_forward(mock_get, monkeypatch):
    # Fake NewsAPI response
    mock_get.return_value.json.return_value = {
        "articles": [
            {"title": "AI News 1", "description": "desc1"},
            {"title": "AI News 2", "description": "desc2"},
        ]
    }
    mock_get.return_value.raise_for_status.return_value = None

    monkeypatch.setenv("NEWS_API_KEY", "fake")
    monkeypatch.setenv("SUMMARIZER_URL", "http://summarizer:5000")

    # Mock forwarding to summarizer
    with patch("collector.app.requests.post") as mock_post:
        mock_post.return_value.json.return_value = [{"title": "AI News 1", "summary": "s1"}]
        mock_post.return_value.raise_for_status.return_value = None

        client = app.test_client()
        resp = client.post("/collect", json={"topic": "ai"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert "summary" in data[0]
