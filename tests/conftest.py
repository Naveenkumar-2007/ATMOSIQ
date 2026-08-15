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
