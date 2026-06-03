"""
Testes da zoser-dummy
"""
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "zoser-dummy"


def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "environment" in data


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"http_requests_total" in response.content