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


def test_combined_weather_handles_incomplete_live_daily_bundle(client):
    import pandas as pd

    import atmosiq.api.app as app_module
    from atmosiq.common.timeutils import now_utc
    from atmosiq.providers.base import ForecastBundle, ProviderMeta

    hourly = pd.DataFrame({
        "time": pd.date_range("2026-08-16", periods=3, freq="h", tz="UTC"),
        "temperature_2m": [28.0, 29.0, 30.0],
        "relative_humidity_2m": [70.0, 68.0, 65.0],
        "wind_speed_10m": [10.0, 11.0, 12.0],
        "weather_code": [0, 1, 2],
    })
    daily = pd.DataFrame({
        "date": pd.date_range("2026-08-16", periods=2, freq="D", tz="UTC"),
    })
    app_module._LIVE_FORECAST_CACHE["kavali"] = (
        9999999999,
        ForecastBundle("kavali", now_utc(), hourly, daily, {}, ProviderMeta(provider="test")),
    )

    response = client.get("/api/v1/weather/combined/kavali")

    app_module._LIVE_FORECAST_CACHE.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["daily"]["temperature_max"] == [31.0, 31.0]


def test_session_uses_fallback_database_when_primary_is_unavailable(tmp_path, monkeypatch):
    from sqlalchemy import text

    from atmosiq.db.session import get_engine

    monkeypatch.setenv("DATABASE_URL", "sqlite:////missing-directory/atmosiq.db")
    monkeypatch.setenv("ATMOSIQ_FALLBACK_DATABASE_URL", f"sqlite:///{tmp_path}/fallback.db")

    engine = get_engine()

    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1
