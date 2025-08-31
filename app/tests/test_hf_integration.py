from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
import app.services.hf_service as hf_service
from app.enums.common import Category
client = TestClient(app)

PRODUCTIVE = Category.productive
UNPRODUCTIVE = Category.unproductive

def test_classify_single_text_hf_mock(monkeypatch):
    monkeypatch.setattr(settings, "USE_HF_CLASSIFIER", True, raising=False)

    def fake_classify_with_hf(text: str):
        # regra simples p/ testar fluxo
        if "relatório" in text.lower():
            return (PRODUCTIVE, 0.85)
        return (UNPRODUCTIVE, 0.77)

    monkeypatch.setattr(hf_service, "classify_with_hf", fake_classify_with_hf, raising=False)

    payload = {"text": "Segue anexo o relatório mensal, confirmem por favor."}
    resp = client.post("/classify", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["category"] == PRODUCTIVE
    assert abs(data["confidence"] - 0.85) < 1e-6
    assert "suggestedReply" in data and isinstance(data["suggestedReply"], str)


def test_classify_batch_hf_mock(monkeypatch):
    monkeypatch.setattr(settings, "USE_HF_CLASSIFIER", True, raising=False)

    def fake_classify_with_hf(text: str):
        return (PRODUCTIVE, 0.9) if "status" in text.lower() else (UNPRODUCTIVE, 0.6)

    monkeypatch.setattr(hf_service, "classify_with_hf", fake_classify_with_hf, raising=False)

    payload = {"texts": [
        "Feliz natal a todos!",
        "Qual o status do meu chamado?",
        "Segue anexo o relatório mensal."
    ]}
    resp = client.post("/classify/batch", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list) and len(data) == 3
    assert data[0]["category"] in (PRODUCTIVE, UNPRODUCTIVE)
    assert isinstance(data[0]["confidence"], float)
    assert isinstance(data[0]["suggestedReply"], str)
