from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import delete

test_env = Path(__file__).resolve().parents[1] / ".env.test"
load_dotenv(test_env, override=True)

# Import after loading the test configuration.
from app.database import engine
from app.models import Issue
from main import app


@pytest.fixture
def client():
    if engine.url.database != "issue_tracker_test":
        raise RuntimeError("Tests require the issue_tracker_test database")

    with engine.begin() as connection:
        connection.execute(delete(Issue))

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        with engine.begin() as connection:
            connection.execute(delete(Issue))
