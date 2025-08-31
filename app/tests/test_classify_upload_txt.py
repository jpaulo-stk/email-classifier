import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_classify_upload_txt():
    content = "Preciso de ajuda com minha senha, por favor."
    files = {"file": ("exemplo.txt", content.encode("utf-8"), "text/plain")}
    resp = client.post("/classify/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "category" in data and "confidence" in data and "suggestedReply" in data
