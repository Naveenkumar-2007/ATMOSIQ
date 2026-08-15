# bootstrap8.py -> run: python bootstrap8.py
import os

W = {}

W["src/atmosiq/constant/training_pipeline/__init__.py"] = r'''
import os

PIPELINE_NAME: str = "AtmosIQ"
ARTIFACT_DIR: str = "artifacts"
CONFIG_FILE_PATH: str = os.path.join("config", "atmosiq.yaml")
SCHEMA_FILE_PATH: str = os.path.join("data_schema", "weather_schema.yaml")

TARGET_COLUMN = "temperature_2m"
TRAIN_FILE_NAME: str = "train.parquet"
VALIDATION_FILE_NAME: str = "validation.parquet"
TEST_FILE_NAME: str = "test.parquet"
PREPROCESSING_OBJECT_FILE_NAME: str = "preprocessor.pkl"
FEATURE_METADATA_FILE_NAME: str = "feature_metadata.json"
MODEL_FILE_NAME: str = "model.pkl"

HORIZONS: list = [1, 3, 6, 12, 24, 48, 72]

# Archive-safe (ERA5) minimal set — these are universally available in Open-Meteo archive.
HISTORICAL_HOURLY_VARIABLES: list = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m",
    "precipitation", "rain", "snowfall",
    "pressure_msl", "surface_pressure", "cloud_cover",
    "wind_speed_10m", "wind_gusts_10m",
]

# Forecast endpoint supports the full set.
HOURLY_VARIABLES: list = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
    "precipitation", "rain", "showers", "snowfall", "precipitation_probability",
    "pressure_msl", "surface_pressure", "cloud_cover", "visibility",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "weather_code",
]

DAILY_VARIABLES: list = [
    "temperature_max", "temperature_min", "precipitation_sum",
    "precipitation_probability_max", "wind_speed_max", "wind_gusts_max",
]

DAILY_HISTORICAL_VARIABLES: list = [
    "temperature_max", "temperature_min", "precipitation_sum",
    "wind_speed_max", "wind_gusts_max",
]

DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_RAW_DIR: str = "raw"
DATA_INGESTION_BRONZE_DIR: str = "bronze"
DATA_INGESTION_FORECAST_DIR: str = "forecasts"

DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_SILVER_DIR: str = "silver"
DATA_VALIDATION_REPORT_FILE_NAME: str = "validation_report.json"

DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_GOLD_DIR: str = "gold"

FEATURE_ENGINEERING_DIR_NAME: str = "feature_engineering"
FEATURE_ENGINEERING_FEATURES_DIR: str = "features"

DATASET_CREATION_DIR_NAME: str = "dataset_creation"
DATASET_MANIFEST_FILE_NAME: str = "dataset_manifest.json"

BASELINE_TRAINER_DIR_NAME: str = "baseline_trainer"
HYPERPARAMETER_TUNER_DIR_NAME: str = "hyperparameter_tuner"
MODEL_TRAINER_DIR_NAME: str = "model_trainer"
DEEP_TRAINER_DIR_NAME: str = "deep_trainer"

MODEL_EVALUATION_DIR_NAME: str = "model_evaluation"
MODEL_EVALUATION_LEADERBOARD_FILE: str = "leaderboard.json"
MODEL_EVALUATION_REPORT_FILE: str = "evaluation_report.json"
MODEL_EVALUATION_ERROR_ANALYSIS_FILE: str = "error_analysis.json"

MODEL_PUSHER_DIR_NAME: str = "model_pusher"
MODEL_PUSHER_GATE_FILE: str = "quality_gate.json"

MONITORING_DIR_NAME: str = "monitoring"
DRIFT_REPORT_FILE_NAME: str = "drift_report.json"
'''

W["src/atmosiq/providers/open_meteo.py"] = r'''
import pandas as pd

from atmosiq.common.timeutils import floor_hour, lead_time_hours, now_utc
from atmosiq.constant.training_pipeline import (
    DAILY_HISTORICAL_VARIABLES, DAILY_VARIABLES, HISTORICAL_HOURLY_VARIABLES, HOURLY_VARIABLES,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.providers.base import ForecastBundle, HistoricalBundle, ProviderMeta, WeatherProvider

logger = logging.getLogger("atmosiq.providers.open_meteo")

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoProvider(WeatherProvider):
    name = "open_meteo"

    def _params(self, location, hourly_vars, daily_vars):
        return {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "hourly": ",".join(hourly_vars),
            "daily": ",".join(daily_vars),
            "timezone": "UTC",
        }

    def _normalize_hourly(self, payload, expected_vars, meta):
        hourly = payload.get("hourly")
        if not hourly or "time" not in hourly:
            raise AtmosIQException(f"Open-Meteo response missing hourly block (request {meta.request_id})")
        times = pd.to_datetime(hourly["time"], utc=True)
        df = pd.DataFrame({"time": times})
        for var in expected_vars:
            if var in hourly:
                df[var] = pd.to_numeric(pd.Series(hourly[var]), errors="coerce")
            else:
                df[var] = float("nan")
        # Ensure all canonical columns exist for downstream consistency.
        for var in HOURLY_VARIABLES:
            if var not in df.columns:
                df[var] = float("nan")
        if "weather_code" in df.columns:
            df["weather_code"] = df["weather_code"].astype("Int64")
        return df

    def _normalize_daily(self, payload):
        daily = payload.get("daily", {})
        if not daily or "time" not in daily:
            return pd.DataFrame()
        df = pd.DataFrame({"date": pd.to_datetime(daily["time"], utc=True)})
        for var in DAILY_VARIABLES:
            if var in daily:
                df[var] = pd.to_numeric(pd.Series(daily[var]), errors="coerce")
            else:
                df[var] = float("nan")
        return df

    def fetch_historical(self, location, start_date, end_date):
        import httpx
        meta = ProviderMeta(provider=self.name, fetched_at=now_utc())
        params = self._params(location, HISTORICAL_HOURLY_VARIABLES, DAILY_HISTORICAL_VARIABLES)
        params.update({"start_date": start_date, "end_date": end_date})
        with httpx.Client() as client:
            raw = self._request_json(client, ARCHIVE_URL, params, meta)
        hourly = self._normalize_hourly(raw, HISTORICAL_HOURLY_VARIABLES, meta)
        daily = self._normalize_daily(raw)
        logger.info("historical fetch ok", extra={"ctx_location_id": location["id"], "ctx_rows": len(hourly)})
        return HistoricalBundle(location["id"], hourly, daily, raw, meta)

    def fetch_forecast(self, location):
        import httpx
        meta = ProviderMeta(provider=self.name, fetched_at=now_utc())
        params = self._params(location, HOURLY_VARIABLES, DAILY_VARIABLES)
        params.update({"forecast_days": 4, "forecast_hours": 96})
        with httpx.Client() as client:
            raw = self._request_json(client, FORECAST_URL, params, meta)
        hourly = self._normalize_hourly(raw, HOURLY_VARIABLES, meta)
        daily = self._normalize_daily(raw)
        issue_time = floor_hour(now_utc())
        hourly["issue_time"] = issue_time
        hourly["valid_time"] = hourly["time"]
        hourly["lead_time_hours"] = hourly["valid_time"].map(
            lambda vt: lead_time_hours(issue_time, vt.to_pydatetime() if hasattr(vt, "to_pydatetime") else vt)
        )
        logger.info("forecast fetch ok", extra={"ctx_location_id": location["id"]})
        return ForecastBundle(location["id"], issue_time, hourly, daily, raw, meta)
'''

# Tighten the historical range to last 1 year so archive responses are smaller + faster.
W["config/atmosiq.yaml"] = r'''
project: AtmosIQ
locations:
  - id: kavali
    name: Kavali
    latitude: 15.4833
    longitude: 79.9167
    timezone: Asia/Kolkata
  - id: hyderabad
    name: Hyderabad
    latitude: 17.3850
    longitude: 78.4867
    timezone: Asia/Kolkata
historical:
  start_date: "2024-01-01"
  end_date: "2026-07-31"
provider:
  name: open_meteo
  timeout_seconds: 60
  max_retries: 3
  backoff_base_seconds: 2.0
splits:
  train: 0.70
  validation: 0.15
  test: 0.15
validation:
  ranges:
    relative_humidity_2m: [0, 100]
    precipitation: [0, 600]
    rain: [0, 600]
    showers: [0, 600]
    snowfall: [0, 300]
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
  max_missing_fraction: 0.20
  max_gap_hours: 12
rain:
  occurrence_threshold_mm: 0.2
  intensity_mm:
    light: 2.5
    moderate: 7.5
    heavy: 64.5
    very_heavy: 115.6
risk:
  heat_feels_like_c:
    elevated: 35
    high: 40
    extreme: 45
  heavy_rain_24h_mm:
    low: 2.5
    medium: 15
    high: 60
    extreme: 120
  wind_gust_kmh:
    low: 30
    medium: 50
    high: 75
quality_gate:
  must_beat_persistence: false
  min_skill_vs_persistence: 0.0
  max_mase: 2.0
  min_rain_pr_auc: 0.40
  min_condition_accuracy: 0.20
  max_latency_ms: 2000.0
  require_manual_approval: false
drift:
  psi_threshold: 0.25
  ks_alpha: 0.05
  confirmation_events: 2
alerts:
  cooldown_minutes: 30
deep:
  sequence_length: 24
  epochs: 5
  batch_size: 64
  patience: 2
tuning:
  n_trials: 5
  cv_splits: 2
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 8 written: {len(W)} files.")