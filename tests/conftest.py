import pytest
from fastapi.testclient import TestClient

from main import app
from app import storage


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIRECTORY", tmp_path)
    monkeypatch.setattr(storage, "DATA_FILE", tmp_path / "issues.json")

    with TestClient(app) as test_client:
        yield test_client
