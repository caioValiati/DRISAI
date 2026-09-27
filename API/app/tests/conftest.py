# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def cliente():
    """Fornece o cliente de testes do FastAPI."""
    return TestClient(app)

@pytest.fixture
def mock_db(mocker):
    """Mocka a sessão do SQLAlchemy para evitar acessos reais ao banco."""
    return mocker.MagicMock()