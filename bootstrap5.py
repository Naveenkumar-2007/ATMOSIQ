# bootstrap5.py -> run: python bootstrap5.py  (overwrites listed files with the expanded scope)
import os

W = {}

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
  must_beat_persistence: true
  min_skill_vs_persistence: 0.05
  max_mase: 0.95
  min_rain_pr_auc: 0.60
  min_condition_accuracy: 0.40
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

W["src/atmosiq/common/weather_codes.py"] = r'''
import math

CONDITION_CLASSES = ["clear", "partly_cloudy", "cloudy", "fog", "rain", "heavy_rain", "snow", "thunderstorm"]
COMPASS_16 = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def weather_code_to_condition(code):
    if code is None:
        return "cloudy"
    try:
        code = int(code)
    except (TypeError, ValueError):
        return "cloudy"
    if code == 0:
        return "clear"
    if code <= 2:
        return "partly_cloudy"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if 51 <= code <= 57 or 61 <= code <= 65:
        return "rain"
    if 66 <= code <= 67 or 80 <= code <= 82:
        return "heavy_rain"
    if 71 <= code <= 77 or code in (85, 86):
        return "snow"
    if code >= 95:
        return "thunderstorm"
    return "cloudy"


def condition_index(code):
    return CONDITION_CLASSES.index(weather_code_to_condition(code))


def compass_index(deg):
    if deg is None:
        return 0
    return int(((float(deg) % 360) / 22.5) + 0.5) % 16


def rain_intensity_category(mm, intensity):
    if mm is None or mm < 0.2:
        return "no_rain"
    if mm < intensity["light"]:
        return "light"
    if mm < intensity["moderate"]:
        return "moderate"
    if mm < intensity["heavy"]:
        return "heavy"
    return "very_heavy"
'''

W["src/atmosiq/components/task_registry.py"] = r'''
TASKS = {
    "temperature": ("temperature_2m", "regression", [1, 3, 6, 12, 24, 48, 72]),
    "apparent_temperature": ("apparent_temperature", "regression", [1, 6, 24]),
    "humidity": ("relative_humidity_2m", "regression", [6, 12, 24]),
    "dew_point": ("dew_point_2m", "regression", [6, 24]),
    "pressure": ("pressure_msl", "regression", [6, 24]),
    "surface_pressure": ("surface_pressure", "regression", [24]),
    "cloud_cover": ("cloud_cover", "regression", [6, 12, 24]),
    "visibility": ("visibility", "regression", [6]),
    "precipitation_amount": ("precipitation", "regression", [1, 6, 24]),
    "rain_occurrence": ("precipitation", "binary", [1, 3, 6, 12, 24]),
    "precipitation_probability": ("precipitation_probability", "regression", [1, 6, 24]),
    "wind_speed": ("wind_speed_10m", "regression", [1, 6, 24, 48]),
    "wind_gusts": ("wind_gusts_10m", "regression", [1, 6, 24]),
    "wind_direction": ("wind_direction_10m", "direction_class", [1, 6, 24]),
    "weather_condition": ("weather_code", "condition_class", [1, 6, 24]),
}


def source_of(task):
    return TASKS[task][0]


def kind_of(task):
    return TASKS[task][1]


def horizons_of(task):
    return TASKS[task][2]


def is_classification(task):
    return kind_of(task) in ("binary", "direction_class", "condition_class")
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


def macro_f1(y, p):
    return float(sk.f1_score(_a(y), _p(p), average="macro", zero_division=0))


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

W["src/atmosiq/components/feature_engineering.py"] = r'''
import os
import sys

import numpy as np
import pandas as pd

from atmosiq.db.models import FeatureVersion
from atmosiq.entity.artifact_entity import DataTransformationArtifact, FeatureEngineeringArtifact
from atmosiq.entity.config_entity import FeatureEngineeringConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.leakage_guard import LeakageGuard
from atmosiq.utils.main_utils.utils import hash_config, read_parquet, save_parquet

logger = logging.getLogger("atmosiq.components.feature_engineering")

TEMP_LAGS = [1, 3, 6, 12, 24, 48]


def _time_features(df):
    t = pd.to_datetime(df["time"], utc=True)
    df = df.copy()
    df["hour"] = t.dt.hour
    df["day"] = t.dt.day
    df["day_of_week"] = t.dt.dayofweek
    df["day_of_year"] = t.dt.dayofyear
    df["week"] = t.dt.isocalendar().week.astype(int)
    df["month"] = t.dt.month
    df["season"] = (t.dt.month % 12 // 3) + 1
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["day_of_year_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
    df["day_of_year_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
    return df


def _lag_rolling_features(df):
    df = df.copy()
    temp = df["temperature_2m"]
    for lag in TEMP_LAGS:
        df[f"temperature_lag_{lag}"] = temp.shift(lag)
    df["humidity_lag_24"] = df["relative_humidity_2m"].shift(24)
    df["pressure_lag_24"] = df["pressure_msl"].shift(24)
    df["wind_lag_24"] = df["wind_speed_10m"].shift(24)
    for window in (3, 6, 24):
        df[f"temperature_mean_{window}h"] = temp.shift(1).rolling(window).mean()
    for window in (6, 24):
        df[f"temperature_std_{window}h"] = temp.shift(1).rolling(window).std()
        df[f"humidity_mean_{window}h"] = df["relative_humidity_2m"].shift(1).rolling(window).mean()
        df[f"wind_mean_{window}h"] = df["wind_speed_10m"].shift(1).rolling(window).mean()
    df["pressure_change_3h"] = df["pressure_msl"] - df["pressure_msl"].shift(3)
    df["pressure_change_6h"] = df["pressure_msl"] - df["pressure_msl"].shift(6)
    df["pressure_tendency"] = df["pressure_msl"] - df["pressure_msl"].shift(1)
    return df


def _physical_features(df):
    df = df.copy()
    df["dew_point_depression"] = df["temperature_2m"] - df["dew_point_2m"]
    df["apparent_temperature_difference"] = df["apparent_temperature"] - df["temperature_2m"]
    df["wind_direction_sin"] = np.sin(np.deg2rad(df["wind_direction_10m"]))
    df["wind_direction_cos"] = np.cos(np.deg2rad(df["wind_direction_10m"]))
    return df


def _provider_forecast_features(df, forecast_df):
    if forecast_df is None or forecast_df.empty:
        return df
    fc = forecast_df.copy()
    rename = {
        "temperature_2m": "provider_temperature_forecast",
        "precipitation": "provider_precipitation_forecast",
        "wind_speed_10m": "provider_wind_forecast",
        "relative_humidity_2m": "provider_humidity_forecast",
        "precipitation_probability": "provider_precip_probability_forecast",
    }
    keep = ["issue_time", "valid_time"] + [c for c in rename if c in fc.columns]
    fc = fc[keep].rename(columns=rename)
    fc["issue_time"] = pd.to_datetime(fc["issue_time"], utc=True)
    fc["valid_time"] = pd.to_datetime(fc["valid_time"], utc=True)
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True)
    merged = pd.merge_asof(df.sort_values("time"), fc.sort_values("valid_time"), left_on="time", right_on="valid_time", direction="backward")
    merged = merged[merged["issue_time"].isna() | (merged["issue_time"] <= merged["time"])]
    merged["provider_forecast_lead_time"] = (merged["valid_time"] - merged["issue_time"]).dt.total_seconds() / 3600
    merged["forecast_issue_time"] = merged["issue_time"]
    merged = merged.drop(columns=["issue_time", "valid_time"])
    err = merged.get("provider_temperature_forecast", pd.Series(dtype=float)) - merged["temperature_2m"]
    merged["recent_provider_bias"] = err.shift(1).rolling(24).mean()
    merged["recent_provider_mae"] = err.abs().shift(1).rolling(24).mean()
    merged["recent_provider_error"] = err.shift(1)
    return merged


def build_features(df, forecast_df=None):
    df = _time_features(df)
    df = _lag_rolling_features(df)
    df = _physical_features(df)
    df = _provider_forecast_features(df, forecast_df)
    return df


class FeatureEngineering:
    def __init__(self, data_transformation_artifact, config, session=None):
        try:
            self.transformation_artifact = data_transformation_artifact
            self.config = config
            self.session = session
            self.guard = LeakageGuard()
        except Exception as e:
            raise AtmosIQException(e, sys)

    def initiate_feature_engineering(self):
        try:
            feature_columns = []
            forecast_root = os.path.normpath(os.path.join(self.transformation_artifact.gold_dir, "..", "..", "data_ingestion", "forecasts"))
            for file_name in sorted(os.listdir(self.transformation_artifact.gold_dir)):
                if not file_name.endswith("_gold.parquet"):
                    continue
                location_id = file_name.replace("_gold.parquet", "")
                df = read_parquet(os.path.join(self.transformation_artifact.gold_dir, file_name))
                fpath = os.path.join(forecast_root, f"{location_id}_forecast.parquet")
                fc = read_parquet(fpath) if os.path.exists(fpath) else None
                df = build_features(df, fc)
                self.guard.assert_lag_columns_causal(df, "time")
                self.guard.assert_forecast_features_causal(df)
                feature_columns = [c for c in df.columns if c not in ("time", "location_id")]
                save_parquet(df, os.path.join(self.config.features_dir, f"{location_id}_features.parquet"))
            version_id = hash_config({"columns": feature_columns, "hash": self.transformation_artifact.config_hash})[:16]
            if self.session is not None:
                self.session.add(FeatureVersion(id=f"feat_{version_id}", feature_columns={"columns": feature_columns}, config_hash=self.transformation_artifact.config_hash))
                self.session.commit()
            logger.info("feature engineering complete", extra={"ctx_n_features": len(feature_columns)})
            return FeatureEngineeringArtifact(
                features_dir=self.config.features_dir,
                feature_version_id=f"feat_{version_id}",
                feature_columns=feature_columns,
                leakage_check_passed=True,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/dataset_creation.py"] = r'''
import os
import sys

import pandas as pd

from atmosiq.common.weather_codes import compass_index, condition_index
from atmosiq.components.task_registry import TASKS, kind_of, source_of
from atmosiq.db.models import DatasetVersion
from atmosiq.entity.artifact_entity import DatasetCreationArtifact, FeatureEngineeringArtifact
from atmosiq.entity.config_entity import DatasetCreationConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.leakage_guard import LeakageGuard
from atmosiq.utils.main_utils.utils import hash_config, read_parquet, save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.dataset_creation")


class DatasetCreation:
    def __init__(self, feature_artifact, config, session=None):
        try:
            self.feature_artifact = feature_artifact
            self.config = config
            self.session = session
            self.guard = LeakageGuard()
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _build_targets(self, df):
        df = df.copy()
        threshold = self.config.app.raw["rain"]["occurrence_threshold_mm"]
        for task, (source, kind, horizons) in TASKS.items():
            future_base = df[source]
            for horizon in horizons:
                future = future_base.shift(-horizon)
                if kind == "regression":
                    col = future
                elif kind == "binary":
                    col = (future > threshold).astype(float)
                elif kind == "condition_class":
                    col = future.map(condition_index)
                elif kind == "direction_class":
                    col = future.map(compass_index)
                else:
                    col = future
                df[f"target_{task}_{horizon}h"] = col
        return df

    def initiate_dataset_creation(self):
        try:
            frames = []
            for file_name in sorted(os.listdir(self.feature_artifact.features_dir)):
                if file_name.endswith("_features.parquet"):
                    frames.append(read_parquet(os.path.join(self.feature_artifact.features_dir, file_name)))
            df = pd.concat(frames, ignore_index=True).sort_values("time").reset_index(drop=True)
            df = self._build_targets(df)
            times = pd.to_datetime(df["time"], utc=True)
            splits = self.config.app.splits
            boundaries = times.quantile([splits["train"], splits["train"] + splits["validation"]])
            train_end, val_end = boundaries.iloc[0], boundaries.iloc[1]
            train = df[times <= train_end]
            validation = df[(times > train_end) & (times <= val_end)]
            test = df[times > val_end]
            for name, part in [("train", train), ("validation", validation), ("test", test)]:
                save_parquet(part, os.path.join(self.config.dataset_dir, f"{name}.parquet"))
            manifest = {
                "feature_version_id": self.feature_artifact.feature_version_id,
                "split_boundaries": {"train_end": str(train_end), "validation_end": str(val_end)},
                "row_counts": {"train": len(train), "validation": len(validation), "test": len(test)},
                "tasks": {t: {"source": s, "kind": k, "horizons": h} for t, (s, k, h) in TASKS.items()},
                "feature_columns": self.feature_artifact.feature_columns,
                "split_policy": "chronological",
            }
            version_id = hash_config(manifest)[:16]
            manifest["dataset_version_id"] = f"ds_{version_id}"
            write_json_file(self.config.manifest_file_path, manifest)
            if self.session is not None:
                self.session.add(DatasetVersion(
                    id=f"ds_{version_id}", dataset_dir=self.config.dataset_dir,
                    split_boundaries=manifest["split_boundaries"], row_counts=manifest["row_counts"], content_hash=version_id,
                ))
                self.session.commit()
            logger.info("dataset created", extra={"ctx_version": f"ds_{version_id}"})
            return DatasetCreationArtifact(
                dataset_dir=self.config.dataset_dir,
                manifest_file_path=self.config.manifest_file_path,
                dataset_version_id=f"ds_{version_id}",
                train_rows=len(train),
                validation_rows=len(validation),
                test_rows=len(test),
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/model_trainer.py"] = r'''
import os
import platform
import sys
import time
import uuid

import pandas as pd

from atmosiq.components.task_registry import TASKS, horizons_of, is_classification
from atmosiq.db.models import TrainingRun
from atmosiq.entity.artifact_entity import DatasetCreationArtifact, FeatureEngineeringArtifact, HyperparameterTunerArtifact, ModelTrainerArtifact
from atmosiq.entity.config_entity import ModelTrainerConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_json_file, read_parquet
from atmosiq.utils.ml_utils.metric import metrics as metric
from atmosiq.utils.ml_utils.model.factory import ModelFactory

logger = logging.getLogger("atmosiq.components.model_trainer")

FEATURE_TOKENS = ("s_", "_lag_", "_mean_", "_std_", "_sin", "_cos")
FEATURE_EXACT = {
    "hour", "day", "day_of_week", "day_of_year", "week", "month", "season",
    "pressure_change_3h", "pressure_change_6h", "pressure_tendency",
    "dew_point_depression", "apparent_temperature_difference",
    "provider_forecast_lead_time", "recent_provider_bias", "recent_provider_mae", "recent_provider_error",
}


def feature_columns_for(df):
    cols = []
    for c in df.columns:
        if c in ("time", "location_id") or c.startswith("target_") or c.startswith("forecast_issue_time"):
            continue
        if c in FEATURE_EXACT or c.startswith(FEATURE_TOKENS) or c.startswith("provider_"):
            cols.append(c)
    return sorted(set(cols))


class ModelTrainer:
    def __init__(self, dataset_artifact, feature_artifact, config, session=None, tuner_artifact=None):
        try:
            self.dataset_artifact = dataset_artifact
            self.feature_artifact = feature_artifact
            self.config = config
            self.session = session
            self.tuner_artifact = tuner_artifact
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _environment(self):
        return {"python": platform.python_version(), "platform": platform.platform(), "packages": {"pandas": pd.__version__}}

    def initiate_model_training(self):
        try:
            train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
            validation = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "validation.parquet"))
            features = feature_columns_for(train)
            artifacts = []
            best_params = read_json_file(self.tuner_artifact.best_params_file_path) if self.tuner_artifact is not None else {}
            for task, (source, kind, horizons) in TASKS.items():
                for horizon in horizons:
                    target_col = f"target_{task}_{horizon}h"
                    avail = [f for f in features if f in train.columns]
                    tr = train.dropna(subset=[target_col] + avail)
                    va = validation.dropna(subset=[target_col] + avail)
                    if tr.empty or va.empty:
                        continue
                    X_tr, y_tr = tr[features].to_numpy(), tr[target_col].to_numpy()
                    X_va, y_va = va[features].to_numpy(), va[target_col].to_numpy()
                    model_names = self.config.rain_classifiers if is_classification(task) else self.config.classical_models
                    for name in model_names:
                        started = time.monotonic()
                        params = best_params.get(f"{name}@{task}@{horizon}", {})
                        model = ModelFactory.create(name, "rain_occurrence" if is_classification(task) else task, params)
                        model.fit(X_tr, y_tr)
                        pred = model.predict(X_va)
                        if is_classification(task):
                            if kind == "binary":
                                proba = model.predict_proba(X_va)
                                val_metrics = {
                                    "accuracy": metric.accuracy(y_va, pred), "precision": metric.precision(y_va, pred),
                                    "recall": metric.recall(y_va, pred), "f1": metric.f1(y_va, pred),
                                    "roc_auc": metric.roc_auc(y_va, proba), "pr_auc": metric.pr_auc(y_va, proba),
                                    "brier": metric.brier_score(y_va, proba), "log_loss": metric.log_loss(y_va, proba),
                                }
                            else:
                                val_metrics = {"accuracy": metric.accuracy(y_va, pred), "macro_f1": metric.macro_f1(y_va, pred)}
                        else:
                            val_metrics = {"mae": metric.mae(y_va, pred), "rmse": metric.rmse(y_va, pred), "r2": metric.r2(y_va, pred)}
                        run_id = f"tr_{uuid.uuid4().hex[:12]}"
                        model_path = os.path.join(self.config.model_trainer_dir, task, f"{horizon}h", f"{name}.pkl")
                        model.save(model_path)
                        if self.session is not None:
                            self.session.add(TrainingRun(
                                id=run_id, model_name=name, task=task, horizon_hours=horizon,
                                dataset_version_id=self.dataset_artifact.dataset_version_id,
                                feature_version_id=self.feature_artifact.feature_version_id,
                                hyperparameters=params, metrics=val_metrics, seed=42,
                                duration_seconds=round(time.monotonic() - started, 2), environment=self._environment(),
                            ))
                            self.session.commit()
                        artifacts.append(ModelTrainerArtifact(
                            trained_model_file_path=model_path, model_name=name, task=task, horizon_hours=horizon,
                            train_metrics={"rows": int(len(tr))}, validation_metrics=val_metrics, training_run_id=run_id,
                        ))
            logger.info("model training complete", extra={"ctx_models": len(artifacts)})
            return artifacts
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/quantile_trainer.py"] = r'''
import os
import sys
import uuid

import numpy as np

from atmosiq.components.model_trainer import feature_columns_for
from atmosiq.components.quantile_models import QuantileEnsemble
from atmosiq.db.models import ModelVersion, TrainingRun
from atmosiq.entity.artifact_entity import DatasetCreationArtifact
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_parquet, save_object
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.quantile_trainer")

QUANTILE_TASKS = [("temperature", 24), ("temperature", 6), ("precipitation_amount", 24)]


class QuantileTrainer:
    def __init__(self, dataset_artifact, config, session=None):
        self.dataset_artifact = dataset_artifact
        self.config = config
        self.session = session

    def initiate_quantile_training(self):
        train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
        validation = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "validation.parquet"))
        features = feature_columns_for(train)
        paths = []
        for task, horizon in QUANTILE_TASKS:
            target_col = f"target_{task}_{horizon}h"
            tr = train.dropna(subset=[target_col] + [f for f in features if f in train.columns])
            va = validation.dropna(subset=[target_col] + [f for f in features if f in validation.columns])
            if tr.empty or va.empty:
                continue
            X_tr, y_tr = tr[features].to_numpy(), tr[target_col].to_numpy()
            X_va, y_va = va[features].to_numpy(), va[target_col].to_numpy()
            ensemble = QuantileEnsemble("lightgbm", (0.1, 0.5, 0.9)).fit(X_tr, y_tr)
            q = ensemble.predict_quantiles(X_va)
            val_metrics = {
                "pinball_10": metric.pinball_loss(y_va, q[:, 0], 0.1),
                "pinball_50": metric.pinball_loss(y_va, q[:, 1], 0.5),
                "pinball_90": metric.pinball_loss(y_va, q[:, 2], 0.9),
                "coverage_10_90": metric.coverage(y_va, q[:, 0], q[:, 2]),
                "interval_width": metric.interval_width(q[:, 0], q[:, 2]),
            }
            run_id = f"tr_{uuid.uuid4().hex[:12]}"
            path = os.path.join(self.config.model_trainer_dir, "quantile", f"{task}_{horizon}h.pkl")
            save_object(path, ensemble)
            if self.session is not None:
                self.session.add(TrainingRun(id=run_id, model_name="quantile_lightgbm", task=f"{task}_quantile", horizon_hours=horizon, dataset_version_id=self.dataset_artifact.dataset_version_id, metrics=val_metrics, seed=42))
                self.session.commit()
                self.session.add(ModelVersion(id=f"mv_{uuid.uuid4().hex[:12]}", model_name="quantile_lightgbm", task=f"{task}_quantile", horizon_hours=horizon, stage="Champion", training_run_id=run_id, artifact_path=path, metrics=val_metrics))
                self.session.commit()
            logger.info("quantile trained", extra={"ctx_task": task, "ctx_horizon": horizon, "ctx_coverage": round(val_metrics["coverage_10_90"], 3)})
            paths.append(path)
        return paths
'''

W["src/atmosiq/components/risk_signals.py"] = r'''
class RiskSignals:
    def __init__(self, risk_config):
        self.cfg = risk_config

    def _level(self, value, bands, higher_is_worse=True):
        if value is None:
            return "normal"
        ordered = ["elevated", "high", "extreme"] if higher_is_worse else ["low", "medium", "high", "extreme"]
        if higher_is_worse:
            if value >= self.cfg["heat_feels_like_c"]["extreme"]:
                return "extreme"
            if value >= self.cfg["heat_feels_like_c"]["high"]:
                return "high"
            if value >= self.cfg["heat_feels_like_c"]["elevated"]:
                return "elevated"
            return "normal"
        return self._band(value)

    def _band(self, value):
        bands = self._bands
        if value >= bands["extreme"]:
            return "extreme"
        if value >= bands["high"]:
            return "high"
        if value >= bands["medium"]:
            return "medium"
        if value >= bands["low"]:
            return "low"
        return "minimal"

    def heat_risk(self, feels_like):
        self._bands = self.cfg["heat_feels_like_c"]
        return {"level": self._band(feels_like), "feels_like_c": feels_like}

    def heavy_rain_risk(self, rain_24h_mm):
        self._bands = self.cfg["heavy_rain_24h_mm"]
        return {"level": self._band(rain_24h_mm), "rain_24h_mm": rain_24h_mm}

    def high_wind_risk(self, gust_kmh):
        self._bands = self.cfg["wind_gust_kmh"]
        return {"level": self._band(gust_kmh), "gust_kmh": gust_kmh}

    def compute(self, feels_like=None, rain_24h_mm=None, gust_kmh=None):
        return {
            "heat": self.heat_risk(feels_like),
            "heavy_rain": self.heavy_rain_risk(rain_24h_mm),
            "high_wind": self.high_wind_risk(gust_kmh),
        }
'''

W["src/atmosiq/components/model_evaluation.py"] = r'''
import os
import sys

import numpy as np
import pandas as pd

from atmosiq.components.model_trainer import feature_columns_for
from atmosiq.components.task_registry import kind_of, is_classification
from atmosiq.entity.artifact_entity import BaselineTrainerArtifact, DatasetCreationArtifact, ModelEvaluationArtifact, ModelTrainerArtifact
from atmosiq.entity.config_entity import ModelEvaluationConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import load_object, read_parquet, write_json_file
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.model_evaluation")

WEATHER_CODE_REGIMES = {
    "clear": lambda r: r.get("weather_code", 0) is not None and r["weather_code"] <= 1,
    "cloudy": lambda r: r.get("weather_code", 0) is not None and 2 <= r["weather_code"] <= 3,
    "rainy": lambda r: r.get("weather_code", 0) is not None and 51 <= r["weather_code"] <= 67,
    "heavy_rain": lambda r: (r.get("weather_code", 0) is not None and 63 <= r["weather_code"] <= 67) or (r.get("precipitation", 0) or 0) >= 7.5,
    "storm": lambda r: r.get("weather_code", 0) is not None and 95 <= r["weather_code"] <= 99,
    "high_wind": lambda r: (r.get("wind_speed_10m", 0) or 0) >= 30,
    "extreme_heat": lambda r: (r.get("temperature_2m", 0) or 0) >= 40,
    "cold": lambda r: (r.get("temperature_2m", 0) or 0) <= 0,
}


def derive_regime(row):
    d = row.to_dict()
    for regime, rule in WEATHER_CODE_REGIMES.items():
        try:
            if rule(d):
                return regime
        except (TypeError, ValueError):
            continue
    return "moderate"


class ModelEvaluation:
    def __init__(self, dataset_artifact, trainer_artifacts, baseline_artifact, config):
        try:
            self.dataset_artifact = dataset_artifact
            self.trainer_artifacts = trainer_artifacts
            self.baseline_artifact = baseline_artifact
            self.config = config
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _evaluate_all(self, test):
        features = feature_columns_for(test)
        board = []
        baseline_df = read_parquet(self.baseline_artifact.baseline_predictions_file_path)
        for artifact in self.trainer_artifacts:
            if artifact.trained_model_file_path.endswith(".pt"):
                continue
            target_col = f"target_{artifact.task}_{artifact.horizon_hours}h"
            usable = test.dropna(subset=[target_col] + [f for f in features if f in test.columns])
            if usable.empty:
                continue
            X = usable[features].to_numpy()
            y = usable[target_col].to_numpy()
            blob = load_object(artifact.trained_model_file_path)
            estimator = blob["estimator"] if isinstance(blob, dict) else blob
            pred = estimator.predict(X)
            base = baseline_df[(baseline_df["model"] == "persistence") & (baseline_df["horizon"] == artifact.horizon_hours)]
            baseline_pred = np.full(len(y), base["prediction"].mean()) if not base.empty else y
            if is_classification(artifact.task):
                if kind_of(artifact.task) == "binary":
                    proba = estimator.predict_proba(X)[:, 1]
                    row = {
                        "model": artifact.model_name, "task": artifact.task, "horizon": artifact.horizon_hours,
                        "accuracy": metric.accuracy(y, pred), "pr_auc": metric.pr_auc(y, proba),
                        "brier": metric.brier_score(y, proba), "f1": metric.f1(y, pred),
                    }
                else:
                    row = {
                        "model": artifact.model_name, "task": artifact.task, "horizon": artifact.horizon_hours,
                        "accuracy": metric.accuracy(y, pred), "macro_f1": metric.macro_f1(y, pred),
                    }
            else:
                row = {
                    "model": artifact.model_name, "task": artifact.task, "horizon": artifact.horizon_hours,
                    "mae": metric.mae(y, pred), "rmse": metric.rmse(y, pred),
                    "mase": metric.mase(y, pred), "skill_vs_persistence": metric.skill_score(y, pred, baseline_pred),
                }
            board.append(row)
        return board

    def _error_analysis(self, test):
        analysis = {"by_hour": {}, "by_month": {}, "by_horizon": {}, "by_regime": {}}
        t = pd.to_datetime(test["time"], utc=True)
        for horizon in self.config.app.horizons:
            col = f"target_temperature_{horizon}h"
            usable = test.dropna(subset=[col])
            if usable.empty:
                continue
            err = (usable["temperature_2m"] - usable[col]).abs()
            analysis["by_horizon"][str(horizon)] = float(err.mean())
        regime = test.apply(derive_regime, axis=1)
        for name, group in test.groupby(regime):
            analysis["by_regime"][str(name)] = int(len(group))
        analysis["by_hour"] = {str(h): int(c) for h, c in t.dt.hour.value_counts().sort_index().items()}
        analysis["by_month"] = {str(m): int(c) for m, c in t.dt.month.value_counts().sort_index().items()}
        return analysis

    def _quality_gate(self, board):
        policy = self.config.app.raw["quality_gate"]
        decisions = []
        for row in board:
            checks = {}
            if row["task"] == "temperature":
                checks["beats_persistence"] = bool(row["skill_vs_persistence"] > 0) if policy["must_beat_persistence"] else True
                checks["mase_ok"] = bool(row["mase"] < policy["max_mase"])
                checks["skill_ok"] = bool(row["skill_vs_persistence"] >= policy["min_skill_vs_persistence"])
            if row["task"] == "rain_occurrence":
                checks["pr_auc_ok"] = bool(row.get("pr_auc", 0) >= policy["min_rain_pr_auc"])
            if row["task"] == "weather_condition":
                checks["accuracy_ok"] = bool(row.get("accuracy", 0) >= policy["min_condition_accuracy"])
            row_passed = all(checks.values()) if checks else True
            decisions.append({"model": row["model"], "task": row["task"], "horizon": row["horizon"], "checks": checks, "passed": row_passed})
        passed_any = any(d["passed"] for d in decisions)
        return {"policy": policy, "decisions": decisions, "passed": passed_any}

    def initiate_model_evaluation(self):
        try:
            test = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "test.parquet"))
            board = self._evaluate_all(test)
            board.sort(key=lambda r: (r["task"], r["horizon"], r.get("mae", 0) or -r.get("accuracy", 0)))
            write_json_file(self.config.leaderboard_file_path, board)
            write_json_file(self.config.error_analysis_file_path, self._error_analysis(test))
            gate = self._quality_gate(board)
            write_json_file(self.config.gate_file_path, gate)
            candidate = ""
            for decision in gate["decisions"]:
                if decision["passed"]:
                    candidate = f"{decision['model']}@{decision['task']}@{decision['horizon']}"
                    break
            report = {"leaderboard_rows": len(board), "gate_passed": gate["passed"], "candidate": candidate}
            write_json_file(self.config.report_file_path, report)
            logger.info("evaluation complete", extra={"ctx_gate": gate["passed"]})
            return ModelEvaluationArtifact(
                leaderboard_file_path=self.config.leaderboard_file_path,
                report_file_path=self.config.report_file_path,
                error_analysis_file_path=self.config.error_analysis_file_path,
                gate_file_path=self.config.gate_file_path,
                gate_passed=gate["passed"],
                champion_candidate=candidate,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/prediction_service.py"] = r'''
import sys
import time
import uuid

import pandas as pd

from atmosiq.common.timeutils import floor_hour, now_utc
from atmosiq.common.weather_codes import COMPASS_16, CONDITION_CLASSES, rain_intensity_category
from atmosiq.components.feature_engineering import build_features
from atmosiq.components.risk_signals import RiskSignals
from atmosiq.components.task_registry import TASKS, horizons_of, is_classification, kind_of
from atmosiq.db.models import ForecastVerification, Location, Prediction
from atmosiq.db.repositories import MonitoringRepository, ObservationRepository
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_prediction_latency_seconds, atmosiq_prediction_total
from atmosiq.observability.tracing import span_ctx
from atmosiq.providers import get_provider
from atmosiq.utils.main_utils.utils import load_object

logger = logging.getLogger("atmosiq.components.prediction_service")


class PredictionService:
    def __init__(self, session, app_config=None):
        self.session = session
        self.repo = MonitoringRepository(session)
        self.app_config = app_config
        self._cache = {}
        self._feature_cache = {}

    def _load_champion(self, task, horizon_hours):
        from atmosiq.db.models import ModelVersion
        key = (task, horizon_hours)
        if key in self._cache:
            return self._cache[key]
        version = (
            self.session.query(ModelVersion)
            .filter_by(task=task, horizon_hours=horizon_hours, stage="Champion")
            .order_by(ModelVersion.created_at.desc())
            .first()
        )
        if version is None:
            raise AtmosIQException(f"No champion for task={task} horizon={horizon_hours}")
        blob = load_object(version.artifact_path)
        self._cache[key] = (version, blob)
        return self._cache[key]

    def _feature_vector(self, location_id):
        if location_id in self._feature_cache:
            return self._feature_cache[location_id]
        loc = self.session.query(Location).filter_by(id=location_id).first()
        if loc is None:
            raise AtmosIQException(f"unknown location {location_id}")
        obs = ObservationRepository(self.session).observations_df(location_id, "open_meteo")
        if obs.empty:
            raise AtmosIQException(f"no observations for {location_id}; run ingestion first")
        provider = get_provider("open_meteo", {})
        forecast = provider.fetch_forecast({"id": loc.id, "latitude": loc.latitude, "longitude": loc.longitude})
        featured = build_features(obs.tail(400), forecast.hourly)
        row = featured.iloc[-1]
        self._feature_cache[location_id] = row
        return row

    def _predict_one(self, task, horizon_hours, location_id):
        version, blob = self._load_champion(task, horizon_hours)
        row = self._feature_vector(location_id)
        estimator = blob["estimator"] if isinstance(blob, dict) else blob
        feature_names = getattr(estimator, "feature_names_in_", None) or list(row.index)
        X = [[float(row.get(f, 0.0) or 0.0) for f in feature_names]]
        raw = estimator.predict(X)[0]
        payload = {"task": task, "horizon_hours": horizon_hours, "model": version.model_name, "model_version": version.id}
        if is_classification(task):
            idx = int(raw)
            if kind_of(task) == "binary":
                proba = float(estimator.predict_proba(X)[0][1])
                payload.update({"rain_probability": proba, "rain_expected": proba >= 0.5, "prediction": proba})
            elif task == "weather_condition":
                payload.update({"condition": CONDITION_CLASSES[idx], "prediction": idx})
            elif task == "wind_direction":
                payload.update({"direction": COMPASS_16[idx], "prediction": idx})
        else:
            payload["prediction"] = float(raw)
        qtask = f"{task}_quantile"
        try:
            qversion, qblob = self._load_champion(qtask, horizon_hours)
            q = qblob.predict_quantiles(X)[0]
            payload.update({"p10": float(q[0]), "p50": float(q[1]), "p90": float(q[2]), "lower": float(q[0]), "upper": float(q[2])})
        except AtmosIQException:
            pass
        return payload

    def predict(self, task, horizon_hours, features=None, location_id=None, issue_time=None):
        request_id = str(uuid.uuid4())
        started = time.monotonic()
        with span_ctx("prediction", {"task": task, "horizon": horizon_hours, "request_id": request_id}):
            try:
                payload = self._predict_one(task, horizon_hours, location_id)
                latency = time.monotonic() - started
                atmosiq_prediction_latency_seconds.labels(task=task, horizon=str(horizon_hours)).observe(latency)
                atmosiq_prediction_total.labels(task=task, horizon=str(horizon_hours), model=payload["model"]).inc()
                issue_time = issue_time or floor_hour(now_utc())
                payload.update({"location": location_id, "forecast_issue_time": issue_time.isoformat()})
                self.repo.add_prediction(Prediction(
                    request_id=request_id, model_version_id=payload["model_version"], location_id=location_id or "unknown",
                    issue_time=issue_time, valid_time=issue_time + pd.Timedelta(hours=horizon_hours),
                    horizon_hours=horizon_hours, task=task, payload=payload,
                ))
                return payload
            except Exception as e:
                raise AtmosIQException(e, sys)

    def predict_full(self, location_id, horizon_hours=24):
        out = {"location": location_id, "horizon_hours": horizon_hours, "tasks": {}}
        for task in TASKS:
            if horizon_hours in horizons_of(task):
                h = horizon_hours
            else:
                h = min(horizons_of(task), key=lambda x: abs(x - horizon_hours))
            try:
                out["tasks"][task] = self._predict_one(task, h, location_id)
            except AtmosIQException:
                out["tasks"][task] = None
        t = out["tasks"]
        rain_mm = (t.get("precipitation_amount") or {}).get("prediction")
        intensity = self.app_config.raw["rain"]["intensity_mm"] if self.app_config else {"light": 2.5, "moderate": 7.5, "heavy": 64.5, "very_heavy": 115.6}
        if rain_mm is not None:
            out["rain_intensity"] = rain_intensity_category(rain_mm, intensity)
        risk = RiskSignals(self.app_config.raw["risk"]) if self.app_config else None
        if risk:
            out["risk"] = risk.compute(
                feels_like=(t.get("apparent_temperature") or {}).get("prediction"),
                rain_24h_mm=rain_mm,
                gust_kmh=(t.get("wind_gusts") or {}).get("prediction"),
            )
        return out
'''

W["src/atmosiq/pipeline/training_pipeline.py"] = r'''
import sys

from atmosiq.components.baseline_trainer import BaselineTrainer
from atmosiq.components.data_ingestion import DataIngestion
from atmosiq.components.data_transformation import DataTransformation
from atmosiq.components.data_validation import DataValidation
from atmosiq.components.dataset_creation import DatasetCreation
from atmosiq.components.deep.trainer import DeepTrainer
from atmosiq.components.feature_engineering import FeatureEngineering
from atmosiq.components.hyperparameter_tuner import HyperparameterTuner
from atmosiq.components.model_evaluation import ModelEvaluation
from atmosiq.components.model_pusher import ModelPusher
from atmosiq.components.model_trainer import ModelTrainer
from atmosiq.components.quantile_trainer import QuantileTrainer
from atmosiq.entity.config_entity import (
    BaselineTrainerConfig, DataIngestionConfig, DataTransformationConfig, DataValidationConfig,
    DatasetCreationConfig, DeepTrainerConfig, FeatureEngineeringConfig, HyperparameterTunerConfig,
    ModelEvaluationConfig, ModelPusherConfig, ModelTrainerConfig, TrainingPipelineConfig,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.providers import get_provider

logger = logging.getLogger("atmosiq.pipeline.training_pipeline")


class TrainingPipeline:
    def __init__(self, session=None, approved_by=None, deep=True, tune=True):
        self.pipeline_config = TrainingPipelineConfig()
        self.session = session
        self.approved_by = approved_by
        self.deep = deep
        self.tune = tune

    def run(self):
        try:
            ingestion_config = DataIngestionConfig(self.pipeline_config)
            app_cfg = ingestion_config.app
            provider = get_provider(app_cfg.raw["provider"]["name"], app_cfg.raw["provider"])

            ingestion_artifact = DataIngestion(ingestion_config, provider, self.session).initiate_data_ingestion()
            validation_artifact = DataValidation(ingestion_artifact, DataValidationConfig(self.pipeline_config), self.session).initiate_data_validation()
            transformation_artifact = DataTransformation(validation_artifact, DataTransformationConfig(self.pipeline_config)).initiate_data_transformation()
            feature_artifact = FeatureEngineering(transformation_artifact, FeatureEngineeringConfig(self.pipeline_config), self.session).initiate_feature_engineering()
            dataset_artifact = DatasetCreation(feature_artifact, DatasetCreationConfig(self.pipeline_config), self.session).initiate_dataset_creation()
            baseline_artifact = BaselineTrainer(dataset_artifact, BaselineTrainerConfig(self.pipeline_config)).initiate_baseline_training()

            tuner_artifact = None
            if self.tune:
                tuner_artifact = HyperparameterTuner(dataset_artifact, HyperparameterTunerConfig(self.pipeline_config)).initiate_tuning()

            trainer_artifacts = ModelTrainer(dataset_artifact, feature_artifact, ModelTrainerConfig(self.pipeline_config), self.session, tuner_artifact).initiate_model_training()
            QuantileTrainer(dataset_artifact, ModelTrainerConfig(self.pipeline_config), self.session).initiate_quantile_training()

            all_artifacts = list(trainer_artifacts)
            if self.deep:
                all_artifacts += DeepTrainer(dataset_artifact, DeepTrainerConfig(self.pipeline_config)).initiate_deep_training()

            evaluation_artifact = ModelEvaluation(dataset_artifact, all_artifacts, baseline_artifact, ModelEvaluationConfig(self.pipeline_config)).initiate_model_evaluation()
            pusher_artifact = ModelPusher(evaluation_artifact, all_artifacts, ModelPusherConfig(self.pipeline_config), self.session, self.approved_by).initiate_model_pusher()

            return {
                "ingestion": ingestion_artifact,
                "validation": validation_artifact,
                "transformation": transformation_artifact,
                "features": feature_artifact,
                "dataset": dataset_artifact,
                "baselines": baseline_artifact,
                "evaluation": evaluation_artifact,
                "pusher": pusher_artifact,
            }
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/pipeline/monitoring_pipeline.py"] = r'''
import sys

import pandas as pd

from atmosiq.common.timeutils import now_utc
from atmosiq.components.alert_manager import AlertManager
from atmosiq.components.drift_monitor import DriftMonitor
from atmosiq.components.performance_monitor import PerformanceMonitor
from atmosiq.components.task_registry import TASKS, source_of
from atmosiq.db.models import ForecastVerification, Prediction, WeatherObservation
from atmosiq.db.repositories import MonitoringRepository, ObservationRepository
from atmosiq.entity.config_entity import AppConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.tracing import span_ctx

logger = logging.getLogger("atmosiq.pipeline.monitoring_pipeline")


class MonitoringPipeline:
    def __init__(self, session):
        self.session = session
        self.app = AppConfig()
        self.repo = MonitoringRepository(session)
        self.drift_monitor = DriftMonitor(session, self.app.raw["drift"]["psi_threshold"], self.app.raw["drift"]["ks_alpha"])
        self.performance_monitor = PerformanceMonitor(session)
        self.alert_manager = AlertManager(session, self.app.raw["alerts"]["cooldown_minutes"])

    def _fetch_reference_current(self, location_id, lookback_hours=720, window_hours=168):
        obs = ObservationRepository(self.session).observations_df(location_id, "open_meteo")
        if obs.empty:
            return None, None
        obs = obs.sort_values("time")
        current = obs.tail(window_hours)
        reference = obs.iloc[:-window_hours] if len(obs) > window_hours else obs.head(max(1, len(obs) - window_hours))
        return reference, current

    def run_drift_checks(self, location_ids, features):
        events = []
        with span_ctx("drift_check"):
            for location_id in location_ids:
                reference, current = self._fetch_reference_current(location_id)
                if reference is None or current is None:
                    continue
                events += self.drift_monitor.check_dataframe(reference, current, features)
        return events

    def run_verification(self):
        now = now_utc()
        preds = self.session.query(Prediction).filter(Prediction.valid_time <= now).order_by(Prediction.created_at.desc()).limit(500).all()
        added = 0
        for p in preds:
            if p.task not in TASKS:
                continue
            exists = self.session.query(ForecastVerification).filter_by(model_version_id=p.model_version_id, task=p.task, valid_time=p.valid_time, location_id=p.location_id).first()
            if exists:
                continue
            obs = self.session.query(WeatherObservation).filter_by(location_id=p.location_id, provider="open_meteo", observation_time=p.valid_time).first()
            if obs is None:
                continue
            actual = getattr(obs, source_of(p.task), None)
            forecast = p.payload.get("prediction")
            if actual is None or forecast is None:
                continue
            self.repo.add_verification(ForecastVerification(
                model_version_id=p.model_version_id, location_id=p.location_id, issue_time=p.issue_time,
                valid_time=p.valid_time, lead_time_hours=p.horizon_hours, task=p.task,
                forecast_value=float(forecast), actual_value=float(actual), error=float(forecast) - float(actual),
            ))
            added += 1
        return added

    def run_performance_checks(self):
        with span_ctx("performance_check"):
            verifications = self.session.query(ForecastVerification).order_by(ForecastVerification.valid_time.desc()).limit(5000).all()
            by_horizon = self.performance_monitor.verify_by_horizon(verifications)
            if verifications:
                df = pd.DataFrame([
                    {"valid_time": v.valid_time, "forecast_value": v.forecast_value, "actual_value": v.actual_value}
                    for v in verifications
                ])
                rolling = self.performance_monitor.rolling_metrics(df)
                return {"by_horizon": by_horizon, "rolling": rolling}
            return {"by_horizon": by_horizon, "rolling": {}}

    def run_cycle(self):
        try:
            verified = self.run_verification()
            features = ["temperature_2m", "relative_humidity_2m", "pressure_msl", "wind_speed_10m"]
            location_ids = [loc["id"] for loc in self.app.locations]
            drift_events = self.run_drift_checks(location_ids, features)
            performance = self.run_performance_checks()
            detected = [e for e in drift_events if e.detected]
            for event in detected:
                self.alert_manager.alert_drift(event.feature)
            for location_id in location_ids:
                latest = ObservationRepository(self.session).latest_observation_time(location_id, "open_meteo")
                if latest is not None:
                    last = latest if latest.tzinfo else latest.replace(tzinfo=now_utc().tzinfo)
                    age_hours = (now_utc() - last).total_seconds() / 3600
                    if age_hours > 24:
                        self.alert_manager.alert_stale_data(location_id, age_hours)
            return {"verified": verified, "drift_events": len(drift_events), "detected": len(detected), "performance": performance}
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/api/app.py"] = r'''
import os
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text

from atmosiq import __version__
from atmosiq.api import schemas
from atmosiq.db.models import Alert, DriftEvent, ForecastVerification, Location, ModelVersion, PerformanceEvent
from atmosiq.db.session import get_session
from atmosiq.entity.config_entity import AppConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_request_latency_seconds, atmosiq_requests_total
from atmosiq.providers import get_provider

logger = logging.getLogger("atmosiq.api")


@asynccontextmanager
async def lifespan(app):
    app.state.db_session = get_session()
    app.state.app_config = AppConfig()
    yield
    app.state.db_session.close()


app = FastAPI(title="AtmosIQ", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AtmosIQException)
async def atmosiq_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"error": "internal_error", "detail": str(exc)[:200]})


@app.middleware("http")
async def instrument(request, call_next):
    import time
    started = time.monotonic()
    response = await call_next(request)
    atmosiq_requests_total.labels(endpoint=request.url.path, method=request.method, status=response.status_code).inc()
    atmosiq_request_latency_seconds.labels(endpoint=request.url.path).observe(time.monotonic() - started)
    return response


@app.get("/health/live", response_model=schemas.HealthResponse)
def health_live():
    return schemas.HealthResponse(status="ok", version=__version__)


@app.get("/health/ready", response_model=schemas.HealthResponse)
def health_ready(request: Request):
    try:
        request.app.state.db_session.execute(text("SELECT 1"))
        return schemas.HealthResponse(status="ready", version=__version__)
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")


@app.get("/api/v1/locations", response_model=list[schemas.LocationOut])
def list_locations(request: Request):
    session = request.app.state.db_session
    locations = session.query(Location).all()
    return [schemas.LocationOut(id=l.id, name=l.name, latitude=l.latitude, longitude=l.longitude, timezone=l.timezone) for l in locations]


@app.get("/api/v1/weather/current/{location_id}", response_model=schemas.CurrentWeatherOut)
def current_weather(location_id, request: Request):
    from atmosiq.db.repositories import ObservationRepository
    df = ObservationRepository(request.app.state.db_session).observations_df(location_id, "open_meteo")
    if df.empty:
        raise HTTPException(status_code=404, detail="no observations for location")
    latest = df.iloc[-1]
    return schemas.CurrentWeatherOut(
        location=location_id, observation_time=str(latest["time"]),
        temperature_2m=latest.get("temperature_2m"), apparent_temperature=latest.get("apparent_temperature"),
        relative_humidity_2m=latest.get("relative_humidity_2m"), wind_speed_10m=latest.get("wind_speed_10m"),
        pressure_msl=latest.get("pressure_msl"), visibility=latest.get("visibility"),
        weather_code=int(latest["weather_code"]) if latest.get("weather_code") is not None else None,
    )


@app.get("/api/v1/weather/hourly/{location_id}", response_model=schemas.HourlyForecastOut)
def hourly_weather(location_id, request: Request):
    from atmosiq.db.repositories import ObservationRepository
    df = ObservationRepository(request.app.state.db_session).observations_df(location_id, "open_meteo").tail(48)
    if df.empty:
        raise HTTPException(status_code=404, detail="no hourly data")
    return schemas.HourlyForecastOut(
        location=location_id, times=df["time"].astype(str).tolist(),
        temperature_2m=[None if pd.isna(v) else float(v) for v in df.get("temperature_2m", [])],
        precipitation=[None if pd.isna(v) else float(v) for v in df.get("precipitation", [])],
        precipitation_probability=[None if pd.isna(v) else float(v) for v in df.get("precipitation_probability", [])],
        wind_speed_10m=[None if pd.isna(v) else float(v) for v in df.get("wind_speed_10m", [])],
    )


@app.get("/api/v1/weather/daily/{location_id}", response_model=schemas.DailyForecastOut)
def daily_weather(location_id, request: Request):
    from atmosiq.db.repositories import ObservationRepository
    df = ObservationRepository(request.app.state.db_session).observations_df(location_id, "open_meteo")
    if df.empty:
        raise HTTPException(status_code=404, detail="no daily data")
    df = df.copy()
    df["date"] = df["time"].dt.date.astype(str)
    daily = df.groupby("date").agg(
        temperature_max=("temperature_2m", "max"), temperature_min=("temperature_2m", "min"),
        precipitation_sum=("precipitation", "sum"), wind_speed_max=("wind_speed_10m", "max"),
    ).reset_index().tail(7)
    return schemas.DailyForecastOut(
        location=location_id, dates=daily["date"].tolist(),
        temperature_max=[None if pd.isna(v) else float(v) for v in daily["temperature_max"]],
        temperature_min=[None if pd.isna(v) else float(v) for v in daily["temperature_min"]],
        precipitation_sum=[None if pd.isna(v) else float(v) for v in daily["precipitation_sum"]],
        precipitation_probability_max=[None] * len(daily),
        wind_speed_max=[None if pd.isna(v) else float(v) for v in daily["wind_speed_max"]],
    )


@app.get("/api/v1/forecast/{location_id}")
def provider_forecast(location_id, request: Request):
    session = request.app.state.db_session
    location = session.query(Location).filter_by(id=location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="location not found")
    provider = get_provider("open_meteo", {})
    bundle = provider.fetch_forecast({"id": location.id, "latitude": location.latitude, "longitude": location.longitude})
    return {"location": location_id, "issue_time": bundle.issue_time.isoformat(), "provider": "open_meteo", "hourly": bundle.hourly.to_dict("records")}


def _service(request: Request):
    from atmosiq.components.prediction_service import PredictionService
    return PredictionService(request.app.state.db_session, request.app.state.app_config)


@app.post("/api/v1/predict/full")
def predict_full(request: Request, location: str = "kavali", horizon_hours: int = 24):
    try:
        return _service(request).predict_full(location, horizon_hours)
    except AtmosIQException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/{task}")
def predict_task(task, request: Request, location: str = "kavali", horizon_hours: int = 24):
    try:
        return _service(request).predict(task, horizon_hours, None, location)
    except AtmosIQException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risk/{location_id}")
def risk(location_id, request: Request, horizon_hours: int = 24):
    full = _service(request).predict_full(location_id, horizon_hours)
    return {"location": location_id, "risk": full.get("risk"), "rain_intensity": full.get("rain_intensity")}


@app.get("/api/v1/verification")
def verification(request: Request):
    session = request.app.state.db_session
    rows = session.query(ForecastVerification).all()
    grouped = {}
    for v in rows:
        key = (v.task, int(v.lead_time_hours))
        grouped.setdefault(key, []).append(v.error if v.error is not None else 0.0)
    out = []
    for (task, lead), errors in sorted(grouped.items()):
        import numpy as np
        arr = np.asarray(errors, dtype=float)
        out.append({"task": task, "horizon_hours": lead, "n": int(len(arr)), "mae": float(np.mean(np.abs(arr))), "rmse": float(np.sqrt(np.mean(arr ** 2))), "bias": float(np.mean(arr))})
    return out


@app.get("/api/v1/models", response_model=list[schemas.ModelOut])
def list_models(request: Request):
    session = request.app.state.db_session
    versions = session.query(ModelVersion).order_by(ModelVersion.created_at.desc()).limit(100).all()
    return [schemas.ModelOut(id=v.id, model_name=v.model_name, task=v.task, horizon_hours=v.horizon_hours, stage=v.stage, location_id=v.location_id) for v in versions]


@app.get("/api/v1/monitoring/summary", response_model=schemas.MonitoringSummaryOut)
def monitoring_summary(request: Request):
    session = request.app.state.db_session
    return schemas.MonitoringSummaryOut(
        active_alerts=session.query(Alert).filter_by(status="open").count(),
        drift_events=session.query(DriftEvent).filter_by(detected=True).count(),
        performance_events=session.query(PerformanceEvent).count(),
        champion_count=session.query(ModelVersion).filter_by(stage="Champion").count(),
    )


@app.get("/api/v1/monitoring/drift", response_model=list[schemas.DriftEventOut])
def monitoring_drift(request: Request):
    session = request.app.state.db_session
    events = session.query(DriftEvent).order_by(DriftEvent.created_at.desc()).limit(100).all()
    return [
        schemas.DriftEventOut(feature=e.feature, reference_period=e.reference_period, current_period=e.current_period, psi=e.psi, ks_statistic=e.ks_statistic, p_value=e.p_value, threshold=e.threshold, detected=e.detected, timestamp=str(e.created_at))
        for e in events
    ]


@app.get("/api/v1/alerts")
def list_alerts(request: Request):
    session = request.app.state.db_session
    alerts = session.query(Alert).order_by(Alert.created_at.desc()).limit(100).all()
    return [
        {"id": a.id, "alert_type": a.alert_type, "severity": a.severity, "scope": a.scope, "message": a.message, "recommendation": a.recommendation, "status": a.status, "created_at": str(a.created_at)}
        for a in alerts
    ]


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


FRONTEND_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 5 written: {len(W)} files.")