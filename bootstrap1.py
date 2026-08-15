# bootstrap1.py  ->  run: python bootstrap1.py   (inside empty AtmosIQ/ dir)
import os

W = {}

W["pyproject.toml"] = r'''
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "atmosiq"
version = "0.1.0"
description = "AtmosIQ - production-oriented weather ML platform (NetworkSecurity architecture + weather ML)"
requires-python = ">=3.11"
dependencies = [
    "numpy>=1.26", "pandas>=2.2", "pyarrow>=15", "scipy>=1.12",
    "scikit-learn>=1.4", "xgboost>=2.0", "lightgbm>=4.3",
    "torch>=2.2", "optuna>=3.6", "mlflow>=2.12",
    "httpx>=0.27", "pyyaml>=6.0", "python-dotenv>=1.0",
    "sqlalchemy>=2.0", "alembic>=1.13", "psycopg[binary]>=3.1",
    "fastapi>=0.110", "uvicorn>=0.29", "pydantic>=2.7",
    "prometheus-client>=0.20", "click>=8.1",
    "opentelemetry-api>=1.24", "opentelemetry-sdk>=1.24",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4", "mypy>=1.10", "pytest-cov>=5.0"]

[project.scripts]
atmosiq = "atmosiq.cli:cli"

[tool.hatch.build.targets.wheel]
packages = ["src/atmosiq"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W", "UP"]

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
'''

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
  start_date: "2023-01-01"
  end_date: "2026-08-10"
provider:
  name: open_meteo
  timeout_seconds: 30
  max_retries: 4
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
  require_manual_approval: true
drift:
  psi_threshold: 0.25
  ks_alpha: 0.05
  confirmation_events: 2
alerts:
  cooldown_minutes: 30
deep:
  sequence_length: 48
  epochs: 30
  batch_size: 128
  patience: 5
tuning:
  n_trials: 40
  cv_splits: 3
'''

W["data_schema/weather_schema.yaml"] = r'''
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
'''

W["alembic.ini"] = r'''
[alembic]
script_location = alembic
sqlalchemy.url =

[loggers]
keys = root
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
'''

W["alembic/env.py"] = r'''
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from atmosiq.db.models import Base
from atmosiq.db.session import database_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", database_url()))
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

W["alembic/versions/0001_initial_schema.py"] = r'''
"""initial schema"""
from alembic import op
from atmosiq.db.models import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
'''

W["src/atmosiq/__init__.py"] = r'''
"""AtmosIQ: production-oriented weather ML platform."""
__version__ = "0.1.0"
'''

W["src/atmosiq/constant/__init__.py"] = r'''
"""Constants package."""
'''

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

W["src/atmosiq/logging/__init__.py"] = r'''
"""Logging package."""
'''

W["src/atmosiq/logging/logger.py"] = r'''
"""Structured JSON logging; components import `logging` from here."""
import logging
import os
import sys
from datetime import datetime, timezone

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = f"{datetime.now(timezone.utc).strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

_REDACT = {"password", "api_key", "token", "secret", "authorization"}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        import json
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in _REDACT:
                continue
            if key.startswith("ctx_"):
                payload[key[4:]] = value
        return json.dumps(payload, default=str)


_hf = logging.FileHandler(LOG_FILE_PATH)
_hf.setFormatter(JsonFormatter())
_hc = logging.StreamHandler(sys.stdout)
_hc.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_hf, _hc])


def get_logger(name):
    return logging.getLogger(name)


def log_event(logger, level, event, **fields):
    logger.log(level, event, **{f"ctx_{k}": v for k, v in fields.items()})
'''

W["src/atmosiq/exception/__init__.py"] = r'''
"""Exception package."""
'''

W["src/atmosiq/exception/exception.py"] = r'''
import sys


class AtmosIQException(Exception):
    def __init__(self, error_message, error_details: sys = sys):
        self.error_message = error_message
        _, _, exc_tb = error_details.exc_info()
        self.lineno = exc_tb.tb_lineno if exc_tb is not None else -1
        self.file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb is not None else "<unknown>"
        super().__init__(str(error_message))

    def __str__(self):
        return "Error occured in python script name [{0}] line number [{1}] error message [{2}]".format(
            self.file_name, self.lineno, str(self.error_message)
        )
'''

W["src/atmosiq/common/__init__.py"] = r'''
"""Common helpers."""
'''

W["src/atmosiq/common/timeutils.py"] = r'''
from datetime import datetime, timedelta, timezone


def now_utc():
    return datetime.now(timezone.utc)


def floor_hour(dt):
    return dt.replace(minute=0, second=0, microsecond=0)


def lead_time_hours(issue_time, valid_time):
    return (valid_time - issue_time) / timedelta(hours=1)
'''

W["src/atmosiq/utils/__init__.py"] = r'''
"""Utils package."""
'''

W["src/atmosiq/utils/main_utils/__init__.py"] = r'''
"""Main utils."""
'''

W["src/atmosiq/utils/main_utils/utils.py"] = r'''
import hashlib
import json
import os
import pickle
import random
import sys

import numpy as np
import pandas as pd
import yaml

from atmosiq.exception.exception import AtmosIQException


def ensure_dir(path):
    target = os.path.dirname(path) if os.path.splitext(path)[1] else path
    if target:
        os.makedirs(target, exist_ok=True)
    return path


def read_yaml_file(file_path):
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise AtmosIQException(e, sys)


def write_yaml_file(file_path, content):
    ensure_dir(file_path)
    with open(file_path, "w") as f:
        yaml.safe_dump(content, f, sort_keys=False)


def read_json_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def write_json_file(file_path, content):
    ensure_dir(file_path)
    with open(file_path, "w") as f:
        json.dump(content, f, indent=2, default=str)


def save_parquet(df, file_path):
    ensure_dir(file_path)
    df.to_parquet(file_path, index=False)


def read_parquet(file_path):
    return pd.read_parquet(file_path)


def hash_config(content):
    return hashlib.sha256(json.dumps(content, sort_keys=True, default=str).encode()).hexdigest()


def save_object(file_path, obj):
    try:
        ensure_dir(file_path)
        blob = pickle.dumps(obj)
        with open(file_path, "wb") as f:
            f.write(blob)
        with open(file_path + ".sha256", "w") as f:
            f.write(hashlib.sha256(blob).hexdigest())
    except Exception as e:
        raise AtmosIQException(e, sys)


def load_object(file_path, trusted_hashes=None):
    try:
        with open(file_path, "rb") as f:
            blob = f.read()
        digest = hashlib.sha256(blob).hexdigest()
        sidecar = file_path + ".sha256"
        if os.path.exists(sidecar):
            with open(sidecar, "r") as f:
                expected = f.read().strip()
            if expected != digest:
                raise ValueError(f"Artifact integrity check failed for {file_path}")
        if trusted_hashes is not None and digest not in trusted_hashes:
            raise ValueError(f"Artifact {file_path} is not in the trusted registry")
        return pickle.loads(blob)
    except Exception as e:
        raise AtmosIQException(e, sys)


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
'''

W["src/atmosiq/utils/ml_utils/__init__.py"] = r'''
"""ML utils."""
'''

W["src/atmosiq/utils/ml_utils/metric/__init__.py"] = r'''
"""Metrics."""
'''

W["src/atmosiq/utils/ml_utils/metric/metrics.py"] = r'''
import numpy as np
from sklearn import metrics as sk


def _a(y):
    return np.asarray(y, dtype=float)


def _p(y):
    return np.asarray(y, dtype=float)


def mae(y, p):
    return float(np.mean(np.abs(_a(y) - _p(p))))


def rmse(y, p):
    return float(np.sqrt(np.mean((_a(y) - _p(p)) ** 2)))


def r2(y, p):
    return float(sk.r2_score(_a(y), _p(p)))


def mase(y, p, seasonal=24):
    y = _a(y); p = _p(p)
    naive = np.mean(np.abs(y[seasonal:] - y[:-seasonal])) if len(y) > seasonal else np.mean(np.abs(np.diff(y)))
    return float(np.mean(np.abs(y - p)) / naive) if naive > 0 else float("inf")


def skill_score(y, p, baseline):
    denom = np.sum((_a(y) - _a(baseline)) ** 2)
    return float(1 - np.sum((_a(y) - _p(p)) ** 2) / denom) if denom > 0 else 0.0


def accuracy(y, p):
    return float(sk.accuracy_score(_a(y), _p(p)))


def precision(y, p):
    return float(sk.precision_score(_a(y), _p(p), zero_division=0))


def recall(y, p):
    return float(sk.recall_score(_a(y), _p(p), zero_division=0))


def f1(y, p):
    return float(sk.f1_score(_a(y), _p(p), zero_division=0))


def roc_auc(y, proba):
    y = _a(y)
    return float(sk.roc_auc_score(y, _p(proba))) if len(np.unique(y)) > 1 else float("nan")


def pr_auc(y, proba):
    y = _a(y)
    if len(np.unique(y)) < 2:
        return float("nan")
    prec, rec, _ = sk.precision_recall_curve(y, _p(proba))
    return float(sk.auc(rec, prec))


def brier_score(y, proba):
    return float(np.mean((_a(y) - _p(proba)) ** 2))


def log_loss(y, proba):
    proba = np.clip(_p(proba), 1e-6, 1 - 1e-6)
    return float(sk.log_loss(_a(y), proba))


def pinball_loss(y, p, quantile):
    y, p = _a(y), _p(p)
    err = y - p
    return float(np.mean(np.where(err >= 0, quantile * err, (quantile - 1) * err)))


def coverage(y, lower, upper):
    return float(np.mean((_a(y) >= _a(lower)) & (_a(y) <= _a(upper))))


def interval_width(lower, upper):
    return float(np.mean(_a(upper) - _a(lower)))


def calibration_error(y, proba, bins=10):
    y, proba = _a(y), _p(proba)
    edges = np.linspace(0, 1, bins + 1)
    errors = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (proba >= lo) & (proba < hi + (1 if hi == 1 else 0))
        if mask.sum() > 0:
            errors.append(abs(y[mask].mean() - proba[mask].mean()))
    return float(np.mean(errors)) if errors else float("nan")
'''

W["src/atmosiq/utils/ml_utils/model/__init__.py"] = r'''
"""Model utils."""
'''

W["src/atmosiq/utils/ml_utils/model/factory.py"] = r'''
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge

from atmosiq.exception.exception import AtmosIQException
from atmosiq.utils.main_utils.utils import load_object, save_object


class ModelWrapper:
    def __init__(self, name, estimator, task, params):
        self.name = name
        self.estimator = estimator
        self.task = task
        self.params = params

    def fit(self, X, y):
        self.estimator.fit(X, y)
        return self

    def predict(self, X):
        return self.estimator.predict(X)

    def predict_proba(self, X):
        if hasattr(self.estimator, "predict_proba"):
            return self.estimator.predict_proba(X)[:, 1]
        raise AtmosIQException(f"{self.name} has no predict_proba")

    def save(self, path):
        save_object(path, {"name": self.name, "task": self.task, "params": self.params, "estimator": self.estimator})

    @staticmethod
    def load(path, trusted_hashes=None):
        blob = load_object(path, trusted_hashes)
        return ModelWrapper(blob["name"], blob["estimator"], blob["task"], blob["params"])

    def metadata(self):
        return {"name": self.name, "task": self.task, "params": self.params}


class PersistenceModel:
    def __init__(self, horizon):
        self.horizon = horizon
        self.name = "persistence"

    def fit(self, X, y):
        return self

    def predict(self, X):
        return np.asarray(X[:, 0], dtype=float)

    def predict_proba(self, X):
        return (np.asarray(X[:, 0], dtype=float) > 0.2).astype(float)

    def save(self, path):
        save_object(path, {"name": self.name, "horizon": self.horizon})

    @staticmethod
    def load(path, trusted_hashes=None):
        return PersistenceModel(load_object(path, trusted_hashes)["horizon"])

    def metadata(self):
        return {"name": self.name, "horizon": self.horizon}


class SeasonalNaiveModel:
    def __init__(self, season_hours=24, column_index=1):
        self.season_hours = season_hours
        self.column_index = column_index
        self.name = f"seasonal_naive_{season_hours}h"

    def fit(self, X, y):
        return self

    def predict(self, X):
        return np.asarray(X[:, self.column_index], dtype=float)

    def predict_proba(self, X):
        return (np.asarray(X[:, self.column_index], dtype=float) > 0.2).astype(float)

    def save(self, path):
        save_object(path, {"name": self.name, "season_hours": self.season_hours, "column_index": self.column_index})

    @staticmethod
    def load(path, trusted_hashes=None):
        blob = load_object(path, trusted_hashes)
        return SeasonalNaiveModel(blob["season_hours"], blob["column_index"])

    def metadata(self):
        return {"name": self.name}


class ClimatologyModel:
    def __init__(self):
        self.name = "climatology"
        self.lookup = {}
        self.fallback = 0.0

    def fit(self, X, y, hour=None, month=None):
        self.fallback = float(np.mean(y))
        if hour is not None and month is not None:
            for h, m, t in zip(hour, month, y):
                self.lookup.setdefault((int(h), int(m)), []).append(float(t))
            self.lookup = {k: float(np.mean(v)) for k, v in self.lookup.items()}
        return self

    def predict(self, X, hour=None, month=None):
        if hour is None:
            return np.full(len(X), self.fallback)
        return np.array([self.lookup.get((int(h), int(m)), self.fallback) for h, m in zip(hour, month)])

    def save(self, path):
        save_object(path, {"name": self.name, "lookup": self.lookup, "fallback": self.fallback})

    @staticmethod
    def load(path, trusted_hashes=None):
        blob = load_object(path, trusted_hashes)
        model = ClimatologyModel()
        model.lookup = {tuple(map(int, k.strip("()").split(", "))): v for k, v in blob["lookup"].items()} if blob["lookup"] else {}
        model.fallback = blob["fallback"]
        return model

    def metadata(self):
        return {"name": self.name}


class ModelFactory:
    REGRESSORS = {
        "linear_regression": lambda p: LinearRegression(),
        "ridge": lambda p: Ridge(**p),
        "random_forest": lambda p: RandomForestRegressor(**p),
        "xgboost": lambda p: __import__("xgboost", fromlist=["XGBRegressor"]).XGBRegressor(**p),
        "lightgbm": lambda p: __import__("lightgbm", fromlist=["LGBMRegressor"]).LGBMRegressor(**p),
    }
    CLASSIFIERS = {
        "logistic_regression": lambda p: LogisticRegression(max_iter=1000, **p),
        "random_forest_clf": lambda p: RandomForestClassifier(**p),
        "xgboost_clf": lambda p: __import__("xgboost", fromlist=["XGBClassifier"]).XGBClassifier(**p),
        "lightgbm_clf": lambda p: __import__("lightgbm", fromlist=["LGBMClassifier"]).LGBMClassifier(**p),
    }

    @classmethod
    def create(cls, name, task, params=None):
        params = params or {}
        table = cls.CLASSIFIERS if task == "rain_occurrence" else cls.REGRESSORS
        if name not in table:
            raise AtmosIQException(f"Unknown model {name} for task {task}")
        return ModelWrapper(name, table[name](params), task, params)

    @classmethod
    def create_baseline(cls, name, horizon):
        if name == "persistence":
            return PersistenceModel(horizon)
        if name == "seasonal_naive_24h":
            return SeasonalNaiveModel(24)
        if name == "seasonal_naive_168h":
            return SeasonalNaiveModel(168)
        if name == "climatology":
            return ClimatologyModel()
        raise AtmosIQException(f"Unknown baseline {name}")
'''

W["src/atmosiq/utils/leakage_guard.py"] = r'''
from datetime import datetime

import pandas as pd

from atmosiq.exception.exception import AtmosIQException


class LeakageViolation(AtmosIQException):
    """Raised when future information leaks into features/targets."""


class LeakageGuard:
    def __init__(self, issue_time=None):
        self.issue_time = issue_time

    def assert_no_future_rows(self, df, time_col, reference=None):
        reference = reference or self.issue_time
        if reference is None:
            return
        times = pd.to_datetime(df[time_col], utc=True)
        future = times[times > pd.Timestamp(reference)]
        if len(future) > 0:
            raise LeakageViolation(f"{len(future)} rows newer than issue_time leaked into features")

    def assert_lag_columns_causal(self, df, time_col):
        suspect = [c for c in df.columns if c.startswith(("lead_", "future_"))]
        if suspect:
            raise LeakageViolation(f"Non-causal columns present: {suspect}")

    def assert_preprocessor_fit_bounds(self, fit_max_time, train_end):
        if fit_max_time > train_end:
            raise LeakageViolation(f"Preprocessor fitted beyond train split end ({fit_max_time} > {train_end})")

    def assert_forecast_features_causal(self, df):
        if {"forecast_issue_time", "time"}.issubset(df.columns):
            bad = df[pd.to_datetime(df["forecast_issue_time"], utc=True) > pd.to_datetime(df["time"], utc=True)]
            if len(bad) > 0:
                raise LeakageViolation("Provider forecast features indexed by issue_time after observation time")

    def assert_target_alignment(self, df, horizon_hours, time_col="time"):
        target_col = f"target_{horizon_hours}h"
        if target_col not in df.columns:
            return
        valid = df.dropna(subset=[target_col])
        if len(valid) == 0:
            return
        last_row_time = pd.to_datetime(valid[time_col], utc=True).max()
        last_target_time = last_row_time + pd.Timedelta(hours=horizon_hours)
        data_end = pd.to_datetime(df[time_col], utc=True).max()
        if last_target_time > data_end + pd.Timedelta(minutes=1):
            raise LeakageViolation("Target references observations beyond available data")
'''

W["src/atmosiq/providers/__init__.py"] = r'''
from atmosiq.providers.base import WeatherProvider
from atmosiq.providers.open_meteo import OpenMeteoProvider

_REGISTRY = {"open_meteo": OpenMeteoProvider}


def get_provider(name, settings=None):
    if name not in _REGISTRY:
        raise ValueError(f"Unknown weather provider: {name}. Known: {sorted(_REGISTRY)}")
    return _REGISTRY[name](settings or {})
'''

W["src/atmosiq/providers/base.py"] = r'''
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging

logger = logging.getLogger("atmosiq.providers")


@dataclass
class ProviderMeta:
    provider: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fetched_at: object = None
    http_status: int = None
    retries: int = 0
    latency_seconds: float = 0.0


@dataclass
class HistoricalBundle:
    location_id: str
    hourly: object
    daily: object
    raw: dict
    meta: ProviderMeta


@dataclass
class ForecastBundle:
    location_id: str
    issue_time: object
    hourly: object
    daily: object
    raw: dict
    meta: ProviderMeta


class WeatherProvider(ABC):
    name = "abstract"

    def __init__(self, settings):
        self.settings = settings
        self.timeout = float(settings.get("timeout_seconds", 30))
        self.max_retries = int(settings.get("max_retries", 4))
        self.backoff_base = float(settings.get("backoff_base_seconds", 2.0))

    def _request_json(self, client, url, params, meta):
        import httpx
        delay = self.backoff_base
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                started = time.monotonic()
                response = client.get(url, params=params, timeout=self.timeout)
                meta.latency_seconds = round(time.monotonic() - started, 3)
                meta.http_status = response.status_code
                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", delay))
                    logger.warning("provider rate limited", extra={"ctx_retry_after": retry_after})
                    time.sleep(retry_after)
                    meta.retries += 1
                    continue
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                last_error = e
                meta.retries += 1
                if attempt < self.max_retries:
                    time.sleep(delay)
                    delay *= 2
        raise AtmosIQException(f"Provider {self.name} request failed: {last_error}")

    @abstractmethod
    def fetch_historical(self, location, start_date, end_date):
        ...

    @abstractmethod
    def fetch_forecast(self, location):
        ...
'''

W["src/atmosiq/providers/open_meteo.py"] = r'''
import pandas as pd

from atmosiq.common.timeutils import floor_hour, lead_time_hours, now_utc
from atmosiq.constant.training_pipeline import DAILY_VARIABLES, HOURLY_VARIABLES
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

    def _normalize_hourly(self, payload, meta):
        hourly = payload.get("hourly")
        if not hourly or "time" not in hourly:
            raise AtmosIQException(f"Open-Meteo response missing hourly block (request {meta.request_id})")
        times = pd.to_datetime(hourly["time"], utc=True)
        df = pd.DataFrame({"time": times})
        for var in HOURLY_VARIABLES:
            if var not in hourly:
                raise AtmosIQException(f"Open-Meteo response missing variable {var}")
            df[var] = pd.to_numeric(pd.Series(hourly[var]), errors="coerce")
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
        return df

    def fetch_historical(self, location, start_date, end_date):
        import httpx
        meta = ProviderMeta(provider=self.name, fetched_at=now_utc())
        params = self._params(location, HOURLY_VARIABLES, DAILY_VARIABLES)
        params.update({"start_date": start_date, "end_date": end_date})
        with httpx.Client() as client:
            raw = self._request_json(client, ARCHIVE_URL, params, meta)
        hourly = self._normalize_hourly(raw, meta)
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
        hourly = self._normalize_hourly(raw, meta)
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

W["src/atmosiq/db/__init__.py"] = r'''
"""Database package."""
'''

W["src/atmosiq/db/session.py"] = r'''
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Dev default is SQLite so the repo runs out-of-the-box; set DATABASE_URL for PostgreSQL in production.
DEFAULT_URL = "sqlite:///atmosiq.db"


def database_url():
    return os.getenv("DATABASE_URL", DEFAULT_URL)


def get_engine(url=None):
    return create_engine(url or database_url(), pool_pre_ping=True)


SessionLocal = sessionmaker(expire_on_commit=False)


def get_session(url=None):
    engine = get_engine(url)
    SessionLocal.configure(bind=engine)
    return SessionLocal()
'''

W["src/atmosiq/db/models.py"] = r'''
"""SQLAlchemy 2.x ORM. Tables created via Alembic in production."""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

TZ = DateTime(timezone=True)


def _now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class WeatherObservation(Base):
    __tablename__ = "weather_observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32))
    observation_time: Mapped[datetime] = mapped_column(TZ)
    temperature_2m: Mapped[float] = mapped_column(Float, nullable=True)
    relative_humidity_2m: Mapped[float] = mapped_column(Float, nullable=True)
    dew_point_2m: Mapped[float] = mapped_column(Float, nullable=True)
    apparent_temperature: Mapped[float] = mapped_column(Float, nullable=True)
    precipitation: Mapped[float] = mapped_column(Float, nullable=True)
    rain: Mapped[float] = mapped_column(Float, nullable=True)
    showers: Mapped[float] = mapped_column(Float, nullable=True)
    snowfall: Mapped[float] = mapped_column(Float, nullable=True)
    precipitation_probability: Mapped[float] = mapped_column(Float, nullable=True)
    pressure_msl: Mapped[float] = mapped_column(Float, nullable=True)
    surface_pressure: Mapped[float] = mapped_column(Float, nullable=True)
    cloud_cover: Mapped[float] = mapped_column(Float, nullable=True)
    visibility: Mapped[float] = mapped_column(Float, nullable=True)
    wind_speed_10m: Mapped[float] = mapped_column(Float, nullable=True)
    wind_direction_10m: Mapped[float] = mapped_column(Float, nullable=True)
    wind_gusts_10m: Mapped[float] = mapped_column(Float, nullable=True)
    weather_code: Mapped[int] = mapped_column(Integer, nullable=True)
    ingestion_time: Mapped[datetime] = mapped_column(TZ, default=_now)
    __table_args__ = (
        UniqueConstraint("location_id", "observation_time", "provider", name="uq_obs_loc_time_provider"),
        Index("ix_obs_time", "location_id", "observation_time"),
    )


class ForecastRun(Base):
    __tablename__ = "weather_forecast_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32))
    issue_time: Mapped[datetime] = mapped_column(TZ)
    request_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)
    __table_args__ = (UniqueConstraint("location_id", "provider", "issue_time", name="uq_run_loc_provider_issue"),)


class Forecast(Base):
    __tablename__ = "weather_forecasts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("weather_forecast_runs.id"))
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), index=True)
    valid_time: Mapped[datetime] = mapped_column(TZ)
    lead_time_hours: Mapped[float] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint("run_id", "location_id", "valid_time", name="uq_forecast_run_loc_valid"),)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    provider: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(TZ)
    finished_at: Mapped[datetime] = mapped_column(TZ, nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    observation_count: Mapped[int] = mapped_column(Integer, default=0)
    forecast_count: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)


class ValidationRun(Base):
    __tablename__ = "validation_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ingestion_run_id: Mapped[str] = mapped_column(ForeignKey("ingestion_runs.id"))
    status: Mapped[str] = mapped_column(String(16))
    rejected_rows: Mapped[int] = mapped_column(Integer, default=0)
    report: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_dir: Mapped[str] = mapped_column(Text)
    split_boundaries: Mapped[dict] = mapped_column(JSON)
    row_counts: Mapped[dict] = mapped_column(JSON)
    content_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class FeatureVersion(Base):
    __tablename__ = "feature_versions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    feature_columns: Mapped[dict] = mapped_column(JSON)
    config_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class TrainingRun(Base):
    __tablename__ = "training_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64))
    task: Mapped[str] = mapped_column(String(32))
    horizon_hours: Mapped[int] = mapped_column(Integer)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id"))
    feature_version_id: Mapped[str] = mapped_column(ForeignKey("feature_versions.id"), nullable=True)
    hyperparameters: Mapped[dict] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
    git_commit: Mapped[str] = mapped_column(String(64), nullable=True)
    seed: Mapped[int] = mapped_column(Integer, default=42)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    environment: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64), index=True)
    task: Mapped[str] = mapped_column(String(32))
    horizon_hours: Mapped[int] = mapped_column(Integer)
    location_id: Mapped[str] = mapped_column(String(32), nullable=True)
    stage: Mapped[str] = mapped_column(String(16), default="Development")
    training_run_id: Mapped[str] = mapped_column(ForeignKey("training_runs.id"))
    artifact_path: Mapped[str] = mapped_column(Text)
    preprocessor_path: Mapped[str] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    issue_time: Mapped[datetime] = mapped_column(TZ)
    valid_time: Mapped[datetime] = mapped_column(TZ)
    horizon_hours: Mapped[int] = mapped_column(Integer)
    task: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class ForecastVerification(Base):
    __tablename__ = "forecast_verifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    issue_time: Mapped[datetime] = mapped_column(TZ)
    valid_time: Mapped[datetime] = mapped_column(TZ)
    lead_time_hours: Mapped[float] = mapped_column(Float)
    task: Mapped[str] = mapped_column(String(32))
    forecast_value: Mapped[float] = mapped_column(Float, nullable=True)
    actual_value: Mapped[float] = mapped_column(Float, nullable=True)
    error: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class DriftEvent(Base):
    __tablename__ = "drift_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature: Mapped[str] = mapped_column(String(64))
    reference_period: Mapped[str] = mapped_column(String(64))
    current_period: Mapped[str] = mapped_column(String(64))
    psi: Mapped[float] = mapped_column(Float, nullable=True)
    ks_statistic: Mapped[float] = mapped_column(Float, nullable=True)
    p_value: Mapped[float] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float)
    detected: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class PerformanceEvent(Base):
    __tablename__ = "performance_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    window_start: Mapped[datetime] = mapped_column(TZ)
    window_end: Mapped[datetime] = mapped_column(TZ)
    metrics: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    scope: Mapped[str] = mapped_column(String(128))
    message: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="open")
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    task: Mapped[str] = mapped_column(String(32))
    horizon_hours: Mapped[int] = mapped_column(Integer)
    location_id: Mapped[str] = mapped_column(String(32), nullable=True)
    action: Mapped[str] = mapped_column(String(16))
    actor: Mapped[str] = mapped_column(String(64), default="system")
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)
'''

W["src/atmosiq/db/repositories.py"] = r'''
"""Repositories: the only place ORM writes happen. No SQL in API routes."""
from sqlalchemy import select
from sqlalchemy.dialects import postgresql, sqlite

from atmosiq.db.models import (
    Alert, Deployment, DriftEvent, Forecast, ForecastRun, ForecastVerification,
    IngestionRun, Location, ModelVersion, PerformanceEvent, Prediction,
    TrainingRun, ValidationRun, WeatherObservation,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging

logger = logging.getLogger("atmosiq.db.repositories")


def _on_conflict_do_nothing(session, model, rows):
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    stmt_cls = postgresql.insert if dialect == "postgresql" else sqlite.insert
    stmt = stmt_cls(model).values(rows)
    for table_arg in model.__table_args__:
        if getattr(table_arg, "name", "") and table_arg.name.startswith("uq_"):
            cols = [col.name for col in table_arg.columns]
            stmt = stmt_cls(model).values(rows).on_conflict_do_nothing(index_elements=cols)
            break
    session.execute(stmt)
    return len(rows)


class LocationRepository:
    def __init__(self, session):
        self.session = session

    def upsert(self, locations):
        for loc in locations:
            if self.session.get(Location, loc["id"]) is None:
                self.session.add(Location(**loc))
        self.session.commit()


class ObservationRepository:
    def __init__(self, session):
        self.session = session

    def upsert_observations(self, location_id, provider, df):
        rows = []
        for record in df.to_dict("records"):
            row = {k: (None if _isna(v) else v) for k, v in record.items() if k != "time"}
            row["location_id"] = location_id
            row["provider"] = provider
            row["observation_time"] = record["time"].to_pydatetime()
            rows.append(row)
        inserted = _on_conflict_do_nothing(self.session, WeatherObservation, rows)
        self.session.commit()
        return inserted

    def latest_observation_time(self, location_id, provider):
        stmt = (
            select(WeatherObservation.observation_time)
            .where(WeatherObservation.location_id == location_id)
            .where(WeatherObservation.provider == provider)
            .order_by(WeatherObservation.observation_time.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def observations_df(self, location_id, provider):
        import pandas as pd
        stmt = (
            select(WeatherObservation)
            .where(WeatherObservation.location_id == location_id)
            .where(WeatherObservation.provider == provider)
            .order_by(WeatherObservation.observation_time)
        )
        objs = self.session.execute(stmt).scalars().all()
        df = pd.DataFrame([
            {c.name: getattr(o, c.name) for c in WeatherObservation.__table__.columns if c.name not in ("id", "ingestion_time")}
            for o in objs
        ])
        if not df.empty:
            df = df.rename(columns={"observation_time": "time"})
            df["time"] = _to_utc(df["time"])
        return df


def _isna(v):
    import pandas as pd
    try:
        return pd.isna(v)
    except (ValueError, TypeError):
        return False


def _to_utc(series):
    import pandas as pd
    s = pd.to_datetime(series, utc=True)
    return s


class ForecastRepository:
    def __init__(self, session):
        self.session = session

    def store_forecast_run(self, location_id, provider, issue_time, request_id, df):
        run = ForecastRun(location_id=location_id, provider=provider, issue_time=issue_time, request_id=request_id)
        self.session.add(run)
        self.session.flush()
        rows = []
        for record in df.to_dict("records"):
            payload = {
                k: (None if _isna(v) else (v.isoformat() if hasattr(v, "isoformat") else v))
                for k, v in record.items()
                if k not in ("time", "issue_time", "valid_time", "lead_time_hours")
            }
            rows.append({
                "run_id": run.id,
                "location_id": location_id,
                "valid_time": record["valid_time"].to_pydatetime(),
                "lead_time_hours": float(record["lead_time_hours"]),
                "payload": payload,
            })
        _on_conflict_do_nothing(self.session, Forecast, rows)
        self.session.commit()
        return len(rows)


class RunRepository:
    def __init__(self, session):
        self.session = session

    def add_ingestion_run(self, run):
        self.session.add(run)
        self.session.commit()

    def add_validation_run(self, run):
        self.session.add(run)
        self.session.commit()

    def add_training_run(self, run):
        self.session.add(run)
        self.session.commit()


class ModelRegistryRepository:
    def __init__(self, session):
        self.session = session

    def add_version(self, version):
        self.session.add(version)
        self.session.commit()

    def champion(self, task, horizon_hours, location_id=None):
        stmt = (
            select(ModelVersion)
            .where(ModelVersion.task == task, ModelVersion.horizon_hours == horizon_hours, ModelVersion.stage == "Champion")
            .order_by(ModelVersion.created_at.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def set_stage(self, version_id, stage):
        version = self.session.get(ModelVersion, version_id)
        if version is None:
            raise AtmosIQException(f"ModelVersion {version_id} not found")
        version.stage = stage
        self.session.commit()

    def add_deployment(self, deployment):
        self.session.add(deployment)
        self.session.commit()


class MonitoringRepository:
    def __init__(self, session):
        self.session = session

    def add_drift_event(self, event):
        self.session.add(event)
        self.session.commit()

    def recent_drift(self, feature, since):
        stmt = select(DriftEvent).where(DriftEvent.feature == feature, DriftEvent.created_at >= since, DriftEvent.detected.is_(True))
        return list(self.session.execute(stmt).scalars().all())

    def add_performance_event(self, event):
        self.session.add(event)
        self.session.commit()

    def add_alert(self, alert):
        self.session.add(alert)
        self.session.commit()

    def latest_alert(self, alert_type, scope):
        stmt = select(Alert).where(Alert.alert_type == alert_type, Alert.scope == scope).order_by(Alert.created_at.desc()).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()

    def add_prediction(self, prediction):
        self.session.add(prediction)
        self.session.commit()

    def add_verification(self, verification):
        self.session.add(verification)
        self.session.commit()
'''

W["src/atmosiq/entity/__init__.py"] = r'''
"""Entity package."""
'''

W["src/atmosiq/entity/config_entity.py"] = r'''
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from atmosiq.constant import training_pipeline as tp
from atmosiq.utils.main_utils.utils import read_yaml_file


@dataclass
class TrainingPipelineConfig:
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%m_%d_%Y_%H_%M_%S"))
    pipeline_name: str = tp.PIPELINE_NAME
    artifact_name: str = tp.ARTIFACT_DIR
    artifact_dir: str = ""

    def __post_init__(self):
        self.artifact_dir = os.path.join(self.artifact_name, self.timestamp)


@dataclass
class AppConfig:
    raw: dict = field(default_factory=lambda: read_yaml_file(tp.CONFIG_FILE_PATH))

    @property
    def locations(self):
        return self.raw["locations"]

    @property
    def horizons(self):
        return self.raw.get("horizons", tp.HORIZONS)

    @property
    def splits(self):
        return self.raw["splits"]


@dataclass
class DataIngestionConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    data_ingestion_dir: str = ""
    raw_dir: str = ""
    bronze_dir: str = ""
    forecast_dir: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATA_INGESTION_DIR_NAME)
        self.data_ingestion_dir = base
        self.raw_dir = os.path.join(base, tp.DATA_INGESTION_RAW_DIR)
        self.bronze_dir = os.path.join(base, tp.DATA_INGESTION_BRONZE_DIR)
        self.forecast_dir = os.path.join(base, tp.DATA_INGESTION_FORECAST_DIR)


@dataclass
class DataValidationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    data_validation_dir: str = ""
    silver_dir: str = ""
    report_file_path: str = ""
    schema_file_path: str = tp.SCHEMA_FILE_PATH

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATA_VALIDATION_DIR_NAME)
        self.data_validation_dir = base
        self.silver_dir = os.path.join(base, tp.DATA_VALIDATION_SILVER_DIR)
        self.report_file_path = os.path.join(base, tp.DATA_VALIDATION_REPORT_FILE_NAME)


@dataclass
class DataTransformationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    data_transformation_dir: str = ""
    gold_dir: str = ""
    preprocessor_file_path: str = ""
    feature_metadata_file_path: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATA_TRANSFORMATION_DIR_NAME)
        self.data_transformation_dir = base
        self.gold_dir = os.path.join(base, tp.DATA_TRANSFORMATION_GOLD_DIR)
        self.preprocessor_file_path = os.path.join(base, tp.PREPROCESSING_OBJECT_FILE_NAME)
        self.feature_metadata_file_path = os.path.join(base, tp.FEATURE_METADATA_FILE_NAME)


@dataclass
class FeatureEngineeringConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    feature_engineering_dir: str = ""
    features_dir: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.FEATURE_ENGINEERING_DIR_NAME)
        self.feature_engineering_dir = base
        self.features_dir = os.path.join(base, tp.FEATURE_ENGINEERING_FEATURES_DIR)


@dataclass
class DatasetCreationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    dataset_dir: str = ""
    manifest_file_path: str = ""

    def __post_init__(self):
        self.dataset_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATASET_CREATION_DIR_NAME)
        self.manifest_file_path = os.path.join(self.dataset_dir, tp.DATASET_MANIFEST_FILE_NAME)


@dataclass
class BaselineTrainerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    baseline_dir: str = ""

    def __post_init__(self):
        self.baseline_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.BASELINE_TRAINER_DIR_NAME)


@dataclass
class HyperparameterTunerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    tuner_dir: str = ""
    n_trials: int = 40
    cv_splits: int = 3

    def __post_init__(self):
        self.tuner_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.HYPERPARAMETER_TUNER_DIR_NAME)
        self.n_trials = int(self.app.raw.get("tuning", {}).get("n_trials", self.n_trials))
        self.cv_splits = int(self.app.raw.get("tuning", {}).get("cv_splits", self.cv_splits))


@dataclass
class ModelTrainerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    model_trainer_dir: str = ""
    classical_models: list = field(default_factory=lambda: ["ridge", "random_forest", "xgboost", "lightgbm"])
    rain_classifiers: list = field(default_factory=lambda: ["logistic_regression", "random_forest_clf", "xgboost_clf", "lightgbm_clf"])

    def __post_init__(self):
        self.model_trainer_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.MODEL_TRAINER_DIR_NAME)


@dataclass
class DeepTrainerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    deep_dir: str = ""
    sequence_length: int = 48
    epochs: int = 30
    batch_size: int = 128
    patience: int = 5

    def __post_init__(self):
        self.deep_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.DEEP_TRAINER_DIR_NAME)
        deep = self.app.raw.get("deep", {})
        self.sequence_length = int(deep.get("sequence_length", self.sequence_length))
        self.epochs = int(deep.get("epochs", self.epochs))
        self.batch_size = int(deep.get("batch_size", self.batch_size))
        self.patience = int(deep.get("patience", self.patience))


@dataclass
class ModelEvaluationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    evaluation_dir: str = ""
    leaderboard_file_path: str = ""
    report_file_path: str = ""
    error_analysis_file_path: str = ""
    gate_file_path: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.MODEL_EVALUATION_DIR_NAME)
        self.evaluation_dir = base
        self.leaderboard_file_path = os.path.join(base, tp.MODEL_EVALUATION_LEADERBOARD_FILE)
        self.report_file_path = os.path.join(base, tp.MODEL_EVALUATION_REPORT_FILE)
        self.error_analysis_file_path = os.path.join(base, tp.MODEL_EVALUATION_ERROR_ANALYSIS_FILE)
        self.gate_file_path = os.path.join(base, tp.MODEL_PUSHER_GATE_FILE)


@dataclass
class ModelPusherConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    pusher_dir: str = ""
    mlflow_tracking_uri: str = ""

    def __post_init__(self):
        import os as _os
        self.pusher_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.MODEL_PUSHER_DIR_NAME)
        self.mlflow_tracking_uri = _os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
'''

W["src/atmosiq/entity/artifact_entity.py"] = r'''
from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    raw_dir: str
    bronze_dir: str
    forecast_dir: str
    ingestion_run_id: str
    observation_count: int
    forecast_count: int


@dataclass
class DataValidationArtifact:
    validation_status: bool
    silver_dir: str
    report_file_path: str
    validation_run_id: str
    rejected_rows: int


@dataclass
class DataTransformationArtifact:
    gold_dir: str
    preprocessor_file_path: str
    feature_metadata_file_path: str
    config_hash: str
    train_split_end: str


@dataclass
class FeatureEngineeringArtifact:
    features_dir: str
    feature_version_id: str
    feature_columns: list
    leakage_check_passed: bool


@dataclass
class DatasetCreationArtifact:
    dataset_dir: str
    manifest_file_path: str
    dataset_version_id: str
    train_rows: int
    validation_rows: int
    test_rows: int


@dataclass
class BaselineTrainerArtifact:
    baseline_dir: str
    baseline_predictions_file_path: str
    baseline_metrics: dict


@dataclass
class HyperparameterTunerArtifact:
    tuner_dir: str
    best_params_file_path: str
    trials_file_path: str
    best_params: dict


@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    model_name: str
    task: str
    horizon_hours: int
    train_metrics: dict
    validation_metrics: dict
    training_run_id: str


@dataclass
class ModelEvaluationArtifact:
    leaderboard_file_path: str
    report_file_path: str
    error_analysis_file_path: str
    gate_file_path: str
    gate_passed: bool
    champion_candidate: str


@dataclass
class ModelPusherArtifact:
    pushed: bool
    model_version_id: str
    stage: str
    message: str
'''

for path, content in W.items():
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 1 written: {len(W)} files.")