"""Pytest konfiguracija i fixtures"""

import pytest
from fastapi.testclient import TestClient

# Ovdje ćemo dodati fixtures kad implementiramo main.py


@pytest.fixture
def client():
    """Test client za FastAPI aplikaciju"""
    from src.main import app

    return TestClient(app)


@pytest.fixture
def mock_dummyjson_response():
    """Mock response from DummyJSON API"""
    return {
        "todos": [
            {
                "id": 1,
                "todo": "Do something nice for someone I care about",
                "completed": True,
                "userId": 26,
            }
        ],
        "total": 150,
        "skip": 0,
        "limit": 30,
    }
