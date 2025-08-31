# app/tests/test_classify.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_classify_single_text():
    payload = {"text": "Segue anexo o relatório mensal, confirmem por favor."}
    resp = client.post("/classify", json=payload)
    print("DEBUG BODY =>", resp.text)
    assert resp.status_code == 200
    data = resp.json()
    assert "category" in data
    assert "confidence" in data
    assert "suggestedReply" in data
    assert isinstance(data["category"], str)
    assert isinstance(data["confidence"], float)
    assert isinstance(data["suggestedReply"], str)
