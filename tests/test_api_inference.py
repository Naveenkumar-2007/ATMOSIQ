import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(sqlite_session, monkeypatch):
    import atmosiq.api.app as app_module

    monkeypatch.setattr(app_module, "get_session", lambda: sqlite_session)
    with TestClient(app_module.app) as c:
        yield c


def test_health_live(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_ready(client):
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_locations_empty(client):
    response = client.get("/api/v1/locations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
