import os

os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "LegalEase"


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_demo():
    payload = {
        "document_type": "NDA",
        "parties": "Alice Smith (Disclosing Party), Example Corp (Receiving Party)",
        "terms": "Confidential information must be protected;15 days termination notice",
        "effective_date": "2026-09-24",
    }
    response = client.post("/api/v1/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "NDA" in body["text"]
    assert body["demo_mode"] is True


def test_txt_export():
    payload = {
        "document_type": "NDA",
        "text": "NON-DISCLOSURE AGREEMENT\nConfidentiality applies.",
    }
    response = client.post("/api/v1/export/txt", json=payload)
    assert response.status_code == 200
    assert b"Confidentiality" in response.content


def test_docx_export():
    payload = {
        "document_type": "NDA",
        "text": "NON-DISCLOSURE AGREEMENT\nConfidentiality applies.",
        "terms": "Confidentiality applies;15 days notice",
    }
    response = client.post("/api/v1/export/docx", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(response.content) > 1000


def test_pdf_export():
    payload = {
        "document_type": "NDA",
        "text": "NON-DISCLOSURE AGREEMENT\nConfidentiality applies.",
        "terms": "Confidentiality applies;15 days notice",
    }
    response = client.post("/api/v1/export/pdf", json=payload)
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
