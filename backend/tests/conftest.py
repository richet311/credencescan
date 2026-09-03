import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def client(monkeypatch):
    # Avoid loading real OCR/ML models during tests: fast, hermetic, no
    # network access or trained-model file required.
    monkeypatch.setattr("app.main.get_reader", lambda: None)
    monkeypatch.setattr("app.main.get_model", lambda: None)

    from app.core.config import settings
    from app.main import app

    monkeypatch.setattr(settings, "demo_username", "testuser")
    monkeypatch.setattr(settings, "demo_password", "testpass")

    with TestClient(app) as test_client:
        yield test_client
