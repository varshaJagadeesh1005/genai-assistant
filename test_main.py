from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app

client = TestClient(app)

def test_ask_endpoint():
    """Verify that the direct /ask endpoint works and returns mock answer."""
    with patch("backend.main.ask", return_value="Mocked answer"):
        res = client.post("/ask", json={"question": "test question"})
        assert res.status_code == 200
        assert "answer" in res.json()
        assert res.json()["answer"] == "Mocked answer"

def test_chat_endpoint():
    """Verify that our custom /api/chat endpoint works and returns mock answer."""
    with patch("backend.main.ask", return_value="Mocked chat response"):
        res = client.post("/api/chat", json={"message": "hello", "use_context": False})
        assert res.status_code == 200
        assert "response" in res.json()
        assert res.json()["response"] == "Mocked chat response"

def test_status_endpoint():
    """Verify that the status endpoint returns server configuration state."""
    res = client.get("/api/status")
    assert res.status_code == 200
    assert "status" in res.json()
    assert res.json()["status"] == "online"
    assert "configured_providers" in res.json()
