from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_classify_batch():
    payload = {"texts": [
        "Feliz natal a todos!",
        "Qual o status do meu chamado?",
        "Segue anexo o relatório mensal."
    ]}
    resp = client.post("/classify/batch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 3
    first = data[0]
    assert "category" in first and "confidence" in first and "suggestedReply" in first
