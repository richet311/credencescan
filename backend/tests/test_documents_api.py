import app.api.routes.documents as documents_module
from app.services.classifier import ClassifierNotTrainedError


def test_upload_rejects_invalid_type(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("bad.txt", b"just plain text", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_success(client, monkeypatch):
    monkeypatch.setattr(
        documents_module,
        "extract_text",
        lambda contents, content_type: "Gross Income: $5000.00\nNet Pay: $3800.00",
    )
    monkeypatch.setattr(
        documents_module,
        "classify_document",
        lambda text: {"document_type": "pay_stub", "confidence": 0.99},
    )

    response = client.post(
        "/api/documents/upload",
        files={"file": ("stub.pdf", b"%PDF-1.4 fake content", "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["document_type"] == "pay_stub"
    assert body["fields"]["gross_income"] == 5000.0
    assert any("withheld" in insight for insight in body["insights"])


def test_upload_handles_untrained_classifier(client, monkeypatch):
    def _raise_not_trained(text):
        raise ClassifierNotTrainedError("not trained")

    monkeypatch.setattr(
        documents_module, "extract_text", lambda contents, content_type: "some text"
    )
    monkeypatch.setattr(documents_module, "classify_document", _raise_not_trained)

    response = client.post(
        "/api/documents/upload",
        files={"file": ("doc.pdf", b"%PDF-1.4 fake content", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["document_type"] is None
