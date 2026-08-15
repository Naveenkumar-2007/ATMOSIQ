# bootstrap7.py -> run: python bootstrap7.py  (patches constants + provider)
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

# Historical (archive/reanalysis) — variables that exist in ERA5.
# precipitation_probability and visibility are forecast-only and cause 400 if requested from archive.
HISTORICAL_HOURLY_VARIABLES: list = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
    "precipitation", "rain", "showers", "snowfall",
    "pressure_msl", "surface_pressure", "cloud_cover",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "weather_code",
]

# Forecast — full variable set including forecast-only variables.
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
            if var not in hourly:
                df[var] = float("nan")
            else:
                df[var] = pd.to_numeric(pd.Series(hourly[var]), errors="coerce")
        for var in ("precipitation_probability", "visibility"):
            if var not in df.columns:
                df[var] = float("nan")
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
        # Use the ERA5-safe subset; forecast-only variables (precipitation_probability, visibility) will be NaN.
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

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 7 written: {len(W)} files.")