# bootstrap3.py  ->  run: python bootstrap3.py   (inside AtmosIQ_/)
import os

W = {}

W["tests/conftest.py"] = r'''
import os
import sys

import pytest

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src")))

CONFIG_YAML = """
project: AtmosIQ
locations:
  - id: kavali
    name: Kavali
    latitude: 15.4833
    longitude: 79.9167
    timezone: Asia/Kolkata
historical:
  start_date: "2023-01-01"
  end_date: "2026-08-10"
provider:
  name: open_meteo
  timeout_seconds: 5
  max_retries: 1
  backoff_base_seconds: 0.1
splits:
  train: 0.70
  validation: 0.15
  test: 0.15
validation:
  ranges:
    relative_humidity_2m: [0, 100]
    precipitation: [0, 600]
    precipitation_probability: [0, 100]
    wind_speed_10m: [0, 150]
    wind_gusts_10m: [0, 200]
    wind_direction_10m: [0, 360]
    pressure_msl: [870, 1085]
    surface_pressure: [400, 1100]
    cloud_cover: [0, 100]
    visibility: [0, 100000]
    temperature_2m: [-90, 60]
    dew_point_2m: [-100, 40]
    apparent_temperature: [-100, 70]
  max_missing_fraction: 0.05
  max_gap_hours: 6
rain:
  occurrence_threshold_mm: 0.2
  heavy_threshold_mm: 7.5
quality_gate:
  must_beat_persistence: true
  min_skill_vs_persistence: 0.05
  max_mase: 0.95
  min_rain_pr_auc: 0.60
  max_latency_ms: 250.0
  require_manual_approval: false
drift:
  psi_threshold: 0.25
  ks_alpha: 0.05
  confirmation_events: 2
alerts:
  cooldown_minutes: 30
deep:
  sequence_length: 8
  epochs: 1
  batch_size: 8
  patience: 1
tuning:
  n_trials: 1
  cv_splits: 2
"""

SCHEMA_YAML = """
canonical_hourly:
  time: datetime64[ns, UTC]
  temperature_2m: float64
  relative_humidity_2m: float64
  dew_point_2m: float64
  apparent_temperature: float64
  precipitation: float64
  rain: float64
  showers: float64
  snowfall: float64
  precipitation_probability: float64
  pressure_msl: float64
  surface_pressure: float64
  cloud_cover: float64
  visibility: float64
  wind_speed_10m: float64
  wind_direction_10m: float64
  wind_gusts_10m: float64
  weather_code: int64
"""


@pytest.fixture
def project_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    os.makedirs("config", exist_ok=True)
    os.makedirs("data_schema", exist_ok=True)
    with open("config/atmosiq.yaml", "w") as f:
        f.write(CONFIG_YAML.lstrip())
    with open("data_schema/weather_schema.yaml", "w") as f:
        f.write(SCHEMA_YAML.lstrip())
    return tmp_path


@pytest.fixture
def sqlite_session(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from atmosiq.db.models import Base

    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def real_observation_df():
    import pandas as pd

    times = pd.date_range("2025-01-01", periods=72, freq="h", tz="UTC")
    return pd.DataFrame({
        "time": times,
        "temperature_2m": [20.0 + (i % 24) * 0.3 for i in range(72)],
        "relative_humidity_2m": [60.0 + (i % 12) for i in range(72)],
        "dew_point_2m": [10.0 + (i % 24) * 0.2 for i in range(72)],
        "apparent_temperature": [21.0 + (i % 24) * 0.3 for i in range(72)],
        "precipitation": [0.0] * 72,
        "rain": [0.0] * 72,
        "showers": [0.0] * 72,
        "snowfall": [0.0] * 72,
        "precipitation_probability": [10.0] * 72,
        "pressure_msl": [1013.0] * 72,
        "surface_pressure": [1010.0] * 72,
        "cloud_cover": [50.0] * 72,
        "visibility": [20000.0] * 72,
        "wind_speed_10m": [5.0] * 72,
        "wind_direction_10m": [180.0] * 72,
        "wind_gusts_10m": [8.0] * 72,
        "weather_code": [1] * 72,
    })
'''

W["tests/test_leakage.py"] = r'''
from datetime import datetime, timezone

import pandas as pd
import pytest

from atmosiq.utils.leakage_guard import LeakageGuard, LeakageViolation


def test_future_rows_detected():
    guard = LeakageGuard(issue_time=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc))
    df = pd.DataFrame({"time": pd.to_datetime(["2025-06-01 13:00"], utc=True)})
    with pytest.raises(LeakageViolation):
        guard.assert_no_future_rows(df, "time")


def test_lead_columns_detected():
    guard = LeakageGuard()
    df = pd.DataFrame({"lead_temperature": [1.0], "time": pd.to_datetime(["2025-06-01"], utc=True)})
    with pytest.raises(LeakageViolation):
        guard.assert_lag_columns_causal(df, "time")


def test_preprocessor_fit_beyond_train():
    guard = LeakageGuard()
    with pytest.raises(LeakageViolation):
        guard.assert_preprocessor_fit_bounds(
            datetime(2025, 7, 1, tzinfo=timezone.utc), datetime(2025, 6, 1, tzinfo=timezone.utc)
        )


def test_causal_data_passes():
    guard = LeakageGuard(issue_time=datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc))
    df = pd.DataFrame({"time": pd.to_datetime(["2025-06-01 10:00", "2025-06-01 11:00"], utc=True)})
    guard.assert_no_future_rows(df, "time")
'''

W["tests/test_validation.py"] = r'''
import os

from atmosiq.components.data_validation import DataValidation
from atmosiq.entity.artifact_entity import DataIngestionArtifact
from atmosiq.entity.config_entity import DataValidationConfig, TrainingPipelineConfig
from atmosiq.utils.main_utils.utils import save_parquet


def _make(project_root, real_observation_df):
    bronze = os.path.join(project_root, "bronze")
    os.makedirs(bronze, exist_ok=True)
    save_parquet(real_observation_df, os.path.join(bronze, "test_hourly.parquet"))
    artifact = DataIngestionArtifact(
        raw_dir="", bronze_dir=bronze, forecast_dir="", ingestion_run_id="t",
        observation_count=len(real_observation_df), forecast_count=0,
    )
    return artifact, DataValidationConfig(TrainingPipelineConfig())


def test_valid_data_passes(project_root, real_observation_df):
    artifact, cfg = _make(project_root, real_observation_df)
    result = DataValidation(artifact, cfg).initiate_data_validation()
    assert result.validation_status is True
    assert result.rejected_rows == 0


def test_out_of_range_rejected(project_root, real_observation_df):
    bad = real_observation_df.copy()
    bad.loc[0, "temperature_2m"] = 200.0
    artifact, cfg = _make(project_root, bad)
    result = DataValidation(artifact, cfg).initiate_data_validation()
    assert result.rejected_rows >= 1
'''

W["tests/test_pipeline_smoke.py"] = r'''
def test_config_loads(project_root):
    from atmosiq.entity.config_entity import AppConfig

    app = AppConfig()
    assert app.locations[0]["id"] == "kavali"
    assert app.horizons[0] == 1
    assert app.splits["train"] == 0.70
    assert app.raw["provider"]["name"] == "open_meteo"
'''

W["tests/test_quality_gate.py"] = r'''
from atmosiq.components.model_evaluation import ModelEvaluation
from atmosiq.entity.config_entity import ModelEvaluationConfig, TrainingPipelineConfig


def _evaluator(project_root):
    cfg = ModelEvaluationConfig(TrainingPipelineConfig())
    return ModelEvaluation(None, [], None, cfg)


def test_gate_blocks_failing_candidate(project_root):
    ev = _evaluator(project_root)
    board = [{"model": "xgboost", "task": "temperature", "horizon": 24, "mae": 1.0, "rmse": 1.5, "mase": 1.2, "skill_vs_persistence": -0.1}]
    gate = ev._quality_gate(board)
    assert gate["passed"] is False


def test_gate_allows_passing_candidate(project_root):
    ev = _evaluator(project_root)
    board = [{"model": "xgboost", "task": "temperature", "horizon": 24, "mae": 1.0, "rmse": 1.5, "mase": 0.5, "skill_vs_persistence": 0.2}]
    gate = ev._quality_gate(board)
    assert gate["passed"] is True
'''

W["tests/test_drift.py"] = r'''
import numpy as np

from atmosiq.components.drift_monitor import compute_psi


def test_psi_detects_shift():
    rng = np.random.default_rng(0)
    reference = rng.normal(20, 2, 1000)
    shifted = rng.normal(30, 2, 1000)
    assert compute_psi(reference, shifted) > 0.25


def test_psi_stable_distribution():
    rng = np.random.default_rng(1)
    reference = rng.normal(20, 2, 1000)
    same = rng.normal(20, 2, 1000)
    assert compute_psi(reference, same) < 0.25
'''

W["tests/test_api_inference.py"] = r'''
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
'''

W["tests/test_db_rollback.py"] = r'''
import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from atmosiq.db.models import Location, WeatherObservation


def test_duplicate_observation_rejected(sqlite_session):
    sqlite_session.add(Location(id="test", name="Test", latitude=15.0, longitude=80.0, timezone="UTC"))
    sqlite_session.commit()
    t = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
    sqlite_session.add(WeatherObservation(location_id="test", provider="open_meteo", observation_time=t, temperature_2m=20.0))
    sqlite_session.commit()
    sqlite_session.add(WeatherObservation(location_id="test", provider="open_meteo", observation_time=t, temperature_2m=21.0))
    with pytest.raises(IntegrityError):
        sqlite_session.commit()
    sqlite_session.rollback()
    assert sqlite_session.query(WeatherObservation).count() == 1
'''

W["frontend/index.html"] = r'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AtmosIQ - Weather ML Platform</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="layout">
    <nav id="sidebar"></nav>
    <main id="content"></main>
  </div>
  <script src="app.js"></script>
</body>
</html>
'''

W["frontend/styles.css"] = r'''
:root {
  --bg: #0f172a;
  --panel: #1e293b;
  --border: #334155;
  --text: #e2e8f0;
  --muted: #94a3b8;
  --accent: #38bdf8;
  --success: #4ade80;
  --warning: #facc15;
  --danger: #f87171;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Inter", system-ui, sans-serif; background: var(--bg); color: var(--text); }
.layout { display: flex; min-height: 100vh; }
#sidebar { width: 240px; background: var(--panel); border-right: 1px solid var(--border); padding: 20px 12px; display: flex; flex-direction: column; gap: 4px; }
#sidebar h1 { font-size: 20px; color: var(--accent); margin-bottom: 20px; }
#sidebar a { color: var(--muted); text-decoration: none; padding: 10px 12px; border-radius: 6px; display: block; font-size: 14px; }
#sidebar a:hover, #sidebar a.active { background: var(--bg); color: var(--accent); }
#content { flex: 1; padding: 28px; overflow-y: auto; }
.page-title { font-size: 24px; margin-bottom: 20px; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 16px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.stat-label { color: var(--muted); font-size: 12px; text-transform: uppercase; }
.stat-value { font-size: 24px; font-weight: 600; margin-top: 4px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border-bottom: 1px solid var(--border); text-align: left; font-size: 14px; }
th { color: var(--muted); font-weight: 500; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }
.badge-success { background: rgba(74,222,128,0.15); color: var(--success); }
.badge-warning { background: rgba(250,204,21,0.15); color: var(--warning); }
.badge-danger { background: rgba(248,113,113,0.15); color: var(--danger); }
.badge-info { background: rgba(56,189,248,0.15); color: var(--accent); }
button, select, input { background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px; font-size: 14px; }
button:hover { border-color: var(--accent); }
'''

W["frontend/app.js"] = r'''
const API_BASE = "";
const PAGES = [
  { route: "/", title: "Overview", render: renderOverview },
  { route: "/current", title: "Current Weather", render: renderCurrent },
  { route: "/hourly", title: "Hourly Forecast", render: renderHourly },
  { route: "/daily", title: "Daily Forecast", render: renderDaily },
  { route: "/rainfall", title: "Rainfall", render: renderRainfall },
  { route: "/wind", title: "Wind", render: renderWind },
  { route: "/models", title: "Models", render: renderModels },
  { route: "/drift", title: "Drift Monitoring", render: renderDrift },
  { route: "/alerts", title: "Alerts", render: renderAlerts },
  { route: "/health", title: "System Health", render: renderHealth },
];

async function api(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(`API ${path} -> ${res.status}`);
  return res.json();
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === "className") node.className = v;
    else if (k === "innerHTML") node.innerHTML = v;
    else node.setAttribute(k, v);
  });
  children.forEach((c) => node.appendChild(typeof c === "string" ? document.createTextNode(c) : c));
  return node;
}

function card(title, body) {
  return el("div", { className: "card" }, [
    el("h3", { innerHTML: title, style: "margin-bottom:12px;color:var(--accent);font-size:16px" }),
    body,
  ]);
}

function table(headers, rows) {
  const thead = el("thead", {}, [el("tr", {}, headers.map((h) => el("th", {}, [h])))]);
  const tbody = el("tbody", {}, rows.map((row) => el("tr", {}, row.map((cell) => el("td", {}, [String(cell)])))));
  return el("table", {}, [thead, tbody]);
}

function badge(text, kind = "info") {
  return el("span", { className: `badge badge-${kind}` }, [text]);
}

async function renderOverview(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Overview"]));
  const grid = el("div", { className: "grid" });
  try {
    const summary = await api("/api/v1/monitoring/summary");
    grid.appendChild(card("Active Alerts", el("div", { className: "stat-value" }, [String(summary.active_alerts)])));
    grid.appendChild(card("Drift Events", el("div", { className: "stat-value" }, [String(summary.drift_events)])));
    grid.appendChild(card("Champion Models", el("div", { className: "stat-value" }, [String(summary.champion_count)])));
    grid.appendChild(card("Performance Events", el("div", { className: "stat-value" }, [String(summary.performance_events)])));
  } catch (e) {
    grid.appendChild(card("Status", el("div", {}, [String(e)])));
  }
  container.appendChild(grid);
}

async function renderCurrent(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Current Weather"]));
  try {
    const locations = await api("/api/v1/locations");
    if (!locations.length) return container.appendChild(el("div", {}, ["No locations configured"]));
    const current = await api(`/api/v1/weather/current/${locations[0].id}`);
    const grid = el("div", { className: "grid" });
    grid.appendChild(card("Temperature", el("div", { className: "stat-value" }, [`${(current.temperature_2m ?? 0).toFixed(1)} C`])));
    grid.appendChild(card("Humidity", el("div", { className: "stat-value" }, [`${(current.relative_humidity_2m ?? 0).toFixed(0)}%`])));
    grid.appendChild(card("Wind", el("div", { className: "stat-value" }, [`${(current.wind_speed_10m ?? 0).toFixed(1)} m/s`])));
    grid.appendChild(card("Pressure", el("div", { className: "stat-value" }, [`${(current.pressure_msl ?? 0).toFixed(0)} hPa`])));
    container.appendChild(grid);
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderHourly(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Hourly Forecast"]));
  try {
    const locations = await api("/api/v1/locations");
    const hourly = await api(`/api/v1/weather/hourly/${locations[0].id}`);
    container.appendChild(table(["Time", "Temp (C)", "Precip (mm)", "Rain Prob (%)", "Wind (m/s)"],
      hourly.times.map((t, i) => [t, hourly.temperature_2m[i], hourly.precipitation[i], hourly.precipitation_probability[i], hourly.wind_speed_10m[i]])));
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderDaily(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Daily Forecast"]));
  try {
    const locations = await api("/api/v1/locations");
    const daily = await api(`/api/v1/weather/daily/${locations[0].id}`);
    container.appendChild(table(["Date", "Max (C)", "Min (C)", "Precip (mm)", "Wind Max (m/s)"],
      daily.dates.map((d, i) => [d, daily.temperature_max[i], daily.temperature_min[i], daily.precipitation_sum[i], daily.wind_speed_max[i]])));
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderRainfall(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Rainfall"]));
  try {
    const locations = await api("/api/v1/locations");
    const daily = await api(`/api/v1/weather/daily/${locations[0].id}`);
    const total = daily.precipitation_sum.reduce((a, b) => a + (b || 0), 0);
    container.appendChild(card("Accumulated Rainfall", el("div", { className: "stat-value" }, [`${total.toFixed(1)} mm`])));
    container.appendChild(table(["Date", "Rainfall (mm)"], daily.dates.map((d, i) => [d, daily.precipitation_sum[i]])));
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderWind(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Wind"]));
  try {
    const locations = await api("/api/v1/locations");
    const hourly = await api(`/api/v1/weather/hourly/${locations[0].id}`);
    container.appendChild(table(["Time", "Wind (m/s)"], hourly.times.map((t, i) => [t, hourly.wind_speed_10m[i]])));
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderModels(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Models"]));
  try {
    const models = await api("/api/v1/models");
    container.appendChild(table(["ID", "Name", "Task", "Horizon", "Stage"], models.map((m) => [
      m.id.slice(0, 12), m.model_name, m.task, `${m.horizon_hours}h`, badge(m.stage, m.stage === "Champion" ? "success" : "info"),
    ])));
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderDrift(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Drift Monitoring"]));
  try {
    const events = await api("/api/v1/monitoring/drift");
    container.appendChild(table(["Feature", "PSI", "KS Stat", "p-value", "Threshold", "Detected", "Timestamp"],
      events.map((e) => [e.feature, e.psi, e.ks_statistic, e.p_value, e.threshold, badge(e.detected ? "yes" : "no", e.detected ? "danger" : "success"), e.timestamp])));
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderAlerts(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["Alerts"]));
  try {
    const alerts = await api("/api/v1/alerts");
    container.appendChild(table(["Severity", "Type", "Scope", "Message", "Status", "Created"],
      alerts.map((a) => [badge(a.severity, a.severity === "CRITICAL" ? "danger" : a.severity === "WARNING" ? "warning" : "info"), a.alert_type, a.scope, a.message, a.status, a.created_at])));
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

async function renderHealth(container) {
  container.appendChild(el("h2", { className: "page-title" }, ["System Health"]));
  try {
    const live = await api("/health/live");
    const ready = await api("/health/ready").catch(() => ({ status: "unavailable" }));
    const grid = el("div", { className: "grid" });
    grid.appendChild(card("Live", el("div", { className: "stat-value" }, [live.status])));
    grid.appendChild(card("Ready", el("div", { className: "stat-value" }, [ready.status])));
    container.appendChild(grid);
  } catch (e) {
    container.appendChild(el("div", {}, [String(e)]));
  }
}

function renderSidebar() {
  const nav = document.getElementById("sidebar");
  nav.appendChild(el("h1", {}, ["AtmosIQ"]));
  PAGES.forEach((p) => nav.appendChild(el("a", { href: `#${p.route}`, "data-route": p.route }, [p.title])));
}

function highlightActive() {
  const path = location.hash.replace(/^#/, "") || "/";
  document.querySelectorAll("#sidebar a").forEach((a) => {
    a.classList.toggle("active", a.getAttribute("data-route") === path);
  });
}

async function router() {
  const path = location.hash.replace(/^#/, "") || "/";
  const page = PAGES.find((p) => p.route === path) || PAGES[0];
  const content = document.getElementById("content");
  content.innerHTML = "";
  highlightActive();
  try {
    await page.render(content);
  } catch (e) {
    content.appendChild(el("div", { className: "card" }, [String(e)]));
  }
}

renderSidebar();
window.addEventListener("hashchange", router);
router();
'''

W["docker/Dockerfile.api"] = r'''
# syntax=docker/dockerfile:1.7
FROM python:3.11.9-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY src ./src
RUN pip install --upgrade pip && pip install --no-cache-dir --prefix=/install .

FROM python:3.11.9-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/install/bin:$PATH" PYTHONPATH=/install/lib/python3.11/site-packages
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r atmosiq && useradd -r -g atmosiq atmosiq
COPY --from=builder /install /install
COPY config ./config
COPY data_schema ./data_schema
COPY alembic.ini ./
COPY alembic ./alembic
COPY frontend ./frontend
USER atmosiq
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health/live || exit 1
CMD ["uvicorn", "atmosiq.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
'''

W["docker/Dockerfile.worker"] = r'''
# syntax=docker/dockerfile:1.7
FROM python:3.11.9-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY src ./src
RUN pip install --upgrade pip && pip install --no-cache-dir --prefix=/install .

FROM python:3.11.9-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/install/bin:$PATH" PYTHONPATH=/install/lib/python3.11/site-packages
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r atmosiq && useradd -r -g atmosiq atmosiq
COPY --from=builder /install /install
COPY config ./config
COPY data_schema ./data_schema
COPY alembic.ini ./
COPY alembic ./alembic
USER atmosiq
CMD ["python", "-m", "atmosiq.worker"]
'''

W["docker/docker-compose.yml"] = r'''
services:
  postgres:
    image: postgres:16.3-alpine
    environment:
      POSTGRES_USER: atmosiq
      POSTGRES_PASSWORD: atmosiq
      POSTGRES_DB: atmosiq
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U atmosiq"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7.2-alpine
    ports: ["6379:6379"]

  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.12.2
    command: mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root /mlflow/artifacts
    ports: ["5000:5000"]
    volumes: [mlflow_data:/mlflow]

  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile.api
    environment:
      DATABASE_URL: postgresql+psycopg://atmosiq:atmosiq@postgres:5432/atmosiq
      MLFLOW_TRACKING_URI: http://mlflow:5000
    ports: ["8000:8000"]
    depends_on:
      postgres:
        condition: service_healthy

  worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile.worker
    environment:
      DATABASE_URL: postgresql+psycopg://atmosiq:atmosiq@postgres:5432/atmosiq
      MLFLOW_TRACKING_URI: http://mlflow:5000
      MONITOR_INTERVAL_SECONDS: "300"
      RETRAIN_INTERVAL_SECONDS: "86400"
    depends_on:
      postgres:
        condition: service_healthy

  prometheus:
    image: prom/prometheus:v2.51.2
    volumes: [./prometheus.yml:/etc/prometheus/prometheus.yml:ro]
    ports: ["9090:9090"]

  grafana:
    image: grafana/grafana:10.4.2
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    ports: ["3000:3000"]
    depends_on: [prometheus]

  jaeger:
    image: jaegertracing/all-in-one:1.57
    ports: ["16686:16686", "4317:4317"]

volumes:
  postgres_data:
  mlflow_data:
'''

W["docker/prometheus.yml"] = r'''
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: atmosiq_api
    metrics_path: /metrics
    static_configs:
      - targets: ["api:8000"]
'''

W[".github/workflows/ci.yml"] = r'''
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint-type-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install
        run: |
          pip install --upgrade pip
          pip install -e .[dev]
      - name: Lint
        run: ruff check src tests
      - name: Type check
        run: mypy src
      - name: Tests
        run: pytest -q

  docker:
    runs-on: ubuntu-latest
    needs: lint-type-test
    steps:
      - uses: actions/checkout@v4
      - name: Build API image
        run: docker build -f docker/Dockerfile.api -t atmosiq-api:test .
      - name: Build worker image
        run: docker build -f docker/Dockerfile.worker -t atmosiq-worker:test .
'''

W[".github/workflows/model-ci.yml"] = r'''
name: Model CI

on:
  pull_request:
    paths: ["src/atmosiq/**", "config/**", "data_schema/**"]

jobs:
  model-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: |
          pip install --upgrade pip
          pip install -e .[dev]
      - name: Leakage tests
        run: pytest tests/test_leakage.py -q
      - name: Validation tests
        run: pytest tests/test_validation.py -q
      - name: Smoke test
        run: pytest tests/test_pipeline_smoke.py -q
      - name: Quality gate tests
        run: pytest tests/test_quality_gate.py -q
'''

W[".github/workflows/deploy.yml"] = r'''
name: Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - name: Build images
        run: |
          docker build -f docker/Dockerfile.api -t atmosiq-api:${{ github.sha }} .
          docker build -f docker/Dockerfile.worker -t atmosiq-worker:${{ github.sha }} .
      - name: Staging smoke test
        if: inputs.environment == 'staging'
        run: echo "Run docker compose + health probe in staging here."
      - name: Production promotion
        if: inputs.environment == 'production'
        run: echo "Production promotion requires manual approval; images built and tagged."
'''

W[".gitignore"] = r'''
# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
build/
dist/
.venv/
venv/

# Data / artifacts / logs (never commit)
artifacts/
logs/
*.db
*.sqlite
*.parquet
mlruns/
mlflow.db
final_model/
saved_models/

# Secrets / env
.env
.env.*
*.pem
*.key

# IDE
.vscode/
.idea/
.DS_Store
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 3 written: {len(W)} files.")