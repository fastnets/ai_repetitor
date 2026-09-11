from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.config import Settings
from app.main import create_app


class FakeLLM:
    def __init__(self):
        self.calls = []

    def chat(self, messages, session_id=None):
        self.calls.append(messages)
        return "Что произошло с количеством предметов: их стало больше или меньше?"


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture
def client(tmp_path, fake_llm):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        textbook_index=tmp_path / "index.json",
        llm_api_key="test",
    )
    app = create_app(settings, fake_llm)
    with TestClient(app) as test_client:
        yield test_client
