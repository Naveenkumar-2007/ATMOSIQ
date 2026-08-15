# bootstrap10.py -> run: python bootstrap10.py
import os

W = {}

# --- 1. India-scale config (24 major cities; expand freely) ---
W["config/atmosiq.yaml"] = r'''
project: AtmosIQ
locations:
  - { id: kavali,      name: Kavali,      latitude: 15.4833, longitude: 79.9167, timezone: Asia/Kolkata }
  - { id: hyderabad,   name: Hyderabad,   latitude: 17.3850, longitude: 78.4867, timezone: Asia/Kolkata }
  - { id: chennai,     name: Chennai,     latitude: 13.0827, longitude: 80.2707, timezone: Asia/Kolkata }
  - { id: bengaluru,   name: Bengaluru,   latitude: 12.9716, longitude: 77.5946, timezone: Asia/Kolkata }
  - { id: mumbai,      name: Mumbai,      latitude: 19.0760, longitude: 72.8777, timezone: Asia/Kolkata }
  - { id: delhi,       name: Delhi,       latitude: 28.7041, longitude: 77.1025, timezone: Asia/Kolkata }
  - { id: kolkata,     name: Kolkata,     latitude: 22.5726, longitude: 88.3639, timezone: Asia/Kolkata }
  - { id: pune,        name: Pune,        latitude: 18.5204, longitude: 73.8567, timezone: Asia/Kolkata }
  - { id: ahmedabad,   name: Ahmedabad,   latitude: 23.0225, longitude: 72.5714, timezone: Asia/Kolkata }
  - { id: jaipur,      name: Jaipur,      latitude: 26.9124, longitude: 75.7873, timezone: Asia/Kolkata }
  - { id: lucknow,     name: Lucknow,     latitude: 26.8467, longitude: 80.9462, timezone: Asia/Kolkata }
  - { id: kanpur,      name: Kanpur,      latitude: 26.4499, longitude: 80.3319, timezone: Asia/Kolkata }
  - { id: nagpur,      name: Nagpur,      latitude: 21.1458, longitude: 79.0882, timezone: Asia/Kolkata }
  - { id: indore,      name: Indore,      latitude: 22.7196, longitude: 75.8577, timezone: Asia/Kolkata }
  - { id: bhopal,      name: Bhopal,      latitude: 23.2599, longitude: 77.4126, timezone: Asia/Kolkata }
  - { id: visakhapatnam, name: Visakhapatnam, latitude: 17.6868, longitude: 83.2185, timezone: Asia/Kolkata }
  - { id: vijayawada,  name: Vijayawada,  latitude: 16.5062, longitude: 80.6480, timezone: Asia/Kolkata }
  - { id: madurai,     name: Madurai,     latitude: 9.9252,  longitude: 78.1198, timezone: Asia/Kolkata }
  - { id: coimbatore,  name: Coimbatore,  latitude: 11.0168, longitude: 76.9558, timezone: Asia/Kolkata }
  - { id: kochi,       name: Kochi,       latitude: 9.9312,  longitude: 76.2673, timezone: Asia/Kolkata }
  - { id: thiruvananthapuram, name: Thiruvananthapuram, latitude: 8.5241, longitude: 76.9366, timezone: Asia/Kolkata }
  - { id: guwahati,    name: Guwahati,    latitude: 26.1445, longitude: 91.7362, timezone: Asia/Kolkata }
  - { id: patna,       name: Patna,       latitude: 25.5941, longitude: 85.1376, timezone: Asia/Kolkata }
  - { id: ranchi,      name: Ranchi,      latitude: 23.3441, longitude: 85.3096, timezone: Asia/Kolkata }
historical:
  start_date: "2024-01-01"
  end_date: "2025-12-31"
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
  max_missing_fraction: 0.25
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
  max_mase: 5.0
  min_rain_pr_auc: 0.30
  min_condition_accuracy: 0.15
  max_latency_ms: 5000.0
  require_manual_approval: false
drift:
  psi_threshold: 0.25
  ks_alpha: 0.05
  confirmation_events: 2
alerts:
  cooldown_minutes: 30
deep:
  sequence_length: 24
  epochs: 3
  batch_size: 64
  patience: 2
tuning:
  n_trials: 5
  cv_splits: 2
'''

# --- 2. Add more production models to the factory ---
W["src/atmosiq/utils/ml_utils/model/factory.py"] = r'''
import numpy as np
from sklearn.ensemble import (
    ExtraTreesClassifier, ExtraTreesRegressor,
    HistGradientBoostingClassifier, HistGradientBoostingRegressor,
    RandomForestClassifier, RandomForestRegressor,
)
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


def _catboost_reg(p):
    try:
        from catboost import CatBoostRegressor
        return CatBoostRegressor(**p, verbose=False)
    except ImportError:
        raise AtmosIQException("catboost not installed; run: pip install catboost")


def _catboost_clf(p):
    try:
        from catboost import CatBoostClassifier
        return CatBoostClassifier(**p, verbose=False)
    except ImportError:
        raise AtmosIQException("catboost not installed; run: pip install catboost")


class ModelFactory:
    REGRESSORS = {
        "linear_regression": lambda p: LinearRegression(),
        "ridge": lambda p: Ridge(**p),
        "random_forest": lambda p: RandomForestRegressor(**p),
        "extra_trees": lambda p: ExtraTreesRegressor(**p),
        "hist_gb": lambda p: HistGradientBoostingRegressor(**p),
        "xgboost": lambda p: __import__("xgboost", fromlist=["XGBRegressor"]).XGBRegressor(**p),
        "lightgbm": lambda p: __import__("lightgbm", fromlist=["LGBMRegressor"]).LGBMRegressor(**p),
        "catboost": _catboost_reg,
    }
    CLASSIFIERS = {
        "logistic_regression": lambda p: LogisticRegression(max_iter=1000, **p),
        "random_forest_clf": lambda p: RandomForestClassifier(**p),
        "extra_trees_clf": lambda p: ExtraTreesClassifier(**p),
        "hist_gb_clf": lambda p: HistGradientBoostingClassifier(**p),
        "xgboost_clf": lambda p: __import__("xgboost", fromlist=["XGBClassifier"]).XGBClassifier(**p),
        "lightgbm_clf": lambda p: __import__("lightgbm", fromlist=["LGBMClassifier"]).LGBMClassifier(**p),
        "catboost_clf": _catboost_clf,
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

# --- 3. Ingestion: attach lat/lon so a GLOBAL India model can learn location ---
W["src/atmosiq/components/data_ingestion.py"] = r'''
import os
import sys
import uuid

from atmosiq.common.timeutils import now_utc
from atmosiq.db.models import IngestionRun
from atmosiq.db.repositories import ForecastRepository, LocationRepository, ObservationRepository, RunRepository
from atmosiq.entity.artifact_entity import DataIngestionArtifact
from atmosiq.entity.config_entity import DataIngestionConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.data_ingestion")


class DataIngestion:
    def __init__(self, data_ingestion_config, provider, session=None):
        try:
            self.config = data_ingestion_config
            self.provider = provider
            self.session = session
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _ingest_location(self, location):
        historical = self.provider.fetch_historical(
            location,
            self.config.app.raw["historical"]["start_date"],
            self.config.app.raw["historical"]["end_date"],
        )
        write_json_file(os.path.join(self.config.raw_dir, f"{location['id']}_historical_raw.json"), historical.raw)
        obs_count = 0
        fc_count = 0
        if self.session is not None:
            LocationRepository(self.session).upsert(self.config.app.locations)
            obs_count = ObservationRepository(self.session).upsert_observations(location["id"], self.provider.name, historical.hourly)
            forecast = self.provider.fetch_forecast(location)
            save_parquet(forecast.hourly, os.path.join(self.config.forecast_dir, f"{location['id']}_forecast.parquet"))
            write_json_file(os.path.join(self.config.forecast_dir, f"{location['id']}_forecast_raw.json"), forecast.raw)
            fc_count = ForecastRepository(self.session).store_forecast_run(location["id"], self.provider.name, forecast.issue_time, forecast.meta.request_id, forecast.hourly)
        # Attach coordinates to the analytical (bronze) copy only, NOT the DB copy.
        bronze = historical.hourly.copy()
        bronze["latitude"] = float(location["latitude"])
        bronze["longitude"] = float(location["longitude"])
        save_parquet(bronze, os.path.join(self.config.bronze_dir, f"{location['id']}_hourly.parquet"))
        if not historical.daily.empty:
            save_parquet(historical.daily, os.path.join(self.config.bronze_dir, f"{location['id']}_daily.parquet"))
        return obs_count, fc_count

    def initiate_data_ingestion(self):
        try:
            run_id = f"ing_{uuid.uuid4().hex[:12]}"
            total_obs = 0
            total_fc = 0
            for location in self.config.app.locations:
                logger.info("ingesting location", extra={"ctx_location_id": location["id"]})
                obs, fc = self._ingest_location(location)
                total_obs += obs
                total_fc += fc
                if self.session is not None:
                    RunRepository(self.session).add_ingestion_run(IngestionRun(
                        id=f"{run_id}_{location['id']}", location_id=location["id"], provider=self.provider.name,
                        started_at=now_utc(), finished_at=now_utc(), status="success",
                        observation_count=obs, forecast_count=fc, meta={"run_id": run_id},
                    ))
            return DataIngestionArtifact(
                raw_dir=self.config.raw_dir, bronze_dir=self.config.bronze_dir, forecast_dir=self.config.forecast_dir,
                ingestion_run_id=run_id, observation_count=total_obs, forecast_count=total_fc,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

# --- 4. Model trainer: use lat/lon as features (global model) ---
W["src/atmosiq/components/model_trainer.py"] = r'''
import os
import platform
import sys
import time
import uuid

import pandas as pd

from atmosiq.components.task_registry import TASKS, is_classification
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
    "latitude", "longitude",
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

# --- 5. Prediction: add lat/lon to the live feature vector ---
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
from atmosiq.db.models import Location, Prediction
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
        obs = obs.copy()
        obs["latitude"] = float(loc.latitude)
        obs["longitude"] = float(loc.longitude)
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
        try:
            qversion, qblob = self._load_champion(f"{task}_quantile", horizon_hours)
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
            h = horizon_hours if horizon_hours in horizons_of(task) else min(horizons_of(task), key=lambda x: abs(x - horizon_hours))
            try:
                out["tasks"][task] = self._predict_one(task, h, location_id)
            except AtmosIQException:
                out["tasks"][task] = None
        t = out["tasks"]
        rain_mm = (t.get("precipitation_amount") or {}).get("prediction")
        intensity = self.app_config.raw["rain"]["intensity_mm"] if self.app_config else {"light": 2.5, "moderate": 7.5, "heavy": 64.5, "very_heavy": 115.6}
        if rain_mm is not None:
            out["rain_intensity"] = rain_intensity_category(rain_mm, intensity)
        if self.app_config:
            out["risk"] = RiskSignals(self.app_config.raw["risk"]).compute(
                feels_like=(t.get("apparent_temperature") or {}).get("prediction"),
                rain_24h_mm=rain_mm,
                gust_kmh=(t.get("wind_gusts") or {}).get("prediction"),
            )
        return out
'''

# --- 6. Report helpers: read the latest leaderboard / champions ---
W["src/atmosiq/report.py"] = r'''
import os

from atmosiq.utils.main_utils.utils import read_json_file


def latest_artifact_dir():
    base = "artifacts"
    if not os.path.isdir(base):
        return None
    ts = sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])
    return os.path.join(base, ts[-1]) if ts else None


def latest_leaderboard():
    d = latest_artifact_dir()
    p = os.path.join(d, "model_evaluation", "leaderboard.json") if d else None
    return read_json_file(p) if p and os.path.exists(p) else []


def print_leaderboard(task=None, horizon=None):
    rows = latest_leaderboard()
    if task:
        rows = [r for r in rows if r.get("task") == task]
    if horizon:
        rows = [r for r in rows if r.get("horizon") == horizon]
    if not rows:
        print("No leaderboard yet. Run: atmosiq train")
        return
    header = f"{'model':<20}{'task':<22}{'hor':>4}  {'mae':>8}  {'rmse':>8}  {'skill':>7}  {'pr_auc':>7}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r.get('model','-'):<20}{r.get('task','-'):<22}{r.get('horizon','-'):>4}  "
              f"{r.get('mae', float('nan')):>8.3f}  {r.get('rmse', float('nan')):>8.3f}  "
              f"{r.get('skill_vs_persistence', float('nan')):>7.2f}  {r.get('pr_auc', float('nan')):>7.2f}")


def print_champions(session):
    from atmosiq.db.models import ModelVersion
    champs = session.query(ModelVersion).filter_by(stage="Champion").order_by(ModelVersion.task, ModelVersion.horizon_hours).all()
    if not champs:
        print("No champions yet.")
        return
    print(f"{'task':<24}{'hor':>4}  {'model':<20}{'version':<16}")
    print("-" * 70)
    for c in champs:
        print(f"{c.task:<24}{c.horizon_hours:>4}  {c.model_name:<20}{c.id:<16}")
'''

# --- 7. API: leaderboard + champions endpoints ---
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
from atmosiq import report as report_mod

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
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
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
    return [schemas.LocationOut(id=l.id, name=l.name, latitude=l.latitude, longitude=l.longitude, timezone=l.timezone)
            for l in session.query(Location).all()]


@app.get("/api/v1/models/leaderboard")
def leaderboard(task: str = None, horizon: int = None):
    rows = report_mod.latest_leaderboard()
    if task:
        rows = [r for r in rows if r.get("task") == task]
    if horizon:
        rows = [r for r in rows if r.get("horizon") == horizon]
    return rows


@app.get("/api/v1/models/champions")
def champions(request: Request):
    session = request.app.state.db_session
    champs = session.query(ModelVersion).filter_by(stage="Champion").order_by(ModelVersion.task, ModelVersion.horizon_hours).all()
    return [{"task": c.task, "horizon_hours": c.horizon_hours, "model": c.model_name, "version": c.id, "metrics": c.metrics} for c in champs]


@app.get("/api/v1/models", response_model=list[schemas.ModelOut])
def list_models(request: Request):
    session = request.app.state.db_session
    versions = session.query(ModelVersion).order_by(ModelVersion.created_at.desc()).limit(100).all()
    return [schemas.ModelOut(id=v.id, model_name=v.model_name, task=v.task, horizon_hours=v.horizon_hours, stage=v.stage, location_id=v.location_id) for v in versions]


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
    import numpy as np
    session = request.app.state.db_session
    rows = session.query(ForecastVerification).all()
    grouped = {}
    for v in rows:
        grouped.setdefault((v.task, int(v.lead_time_hours)), []).append(v.error if v.error is not None else 0.0)
    out = []
    for (task, lead), errors in sorted(grouped.items()):
        arr = np.asarray(errors, dtype=float)
        out.append({"task": task, "horizon_hours": lead, "n": int(len(arr)),
                    "mae": float(np.mean(np.abs(arr))), "rmse": float(np.sqrt(np.mean(arr ** 2))), "bias": float(np.mean(arr))})
    return out


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
    return [schemas.DriftEventOut(feature=e.feature, reference_period=e.reference_period, current_period=e.current_period,
            psi=e.psi, ks_statistic=e.ks_statistic, p_value=e.p_value, threshold=e.threshold, detected=e.detected, timestamp=str(e.created_at))
            for e in events]


@app.get("/api/v1/alerts")
def list_alerts(request: Request):
    session = request.app.state.db_session
    alerts = session.query(Alert).order_by(Alert.created_at.desc()).limit(100).all()
    return [{"id": a.id, "alert_type": a.alert_type, "severity": a.severity, "scope": a.scope, "message": a.message,
             "recommendation": a.recommendation, "status": a.status, "created_at": str(a.created_at)} for a in alerts]


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


FRONTEND_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
'''

# --- 8. Leaderboard chart page ---
W["frontend/leaderboard.html"] = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>AtmosIQ - Model Leaderboard</title>
<style>
body{font-family:Inter,Segoe UI,sans-serif;background:#0b1220;color:#e6edf7;margin:0;padding:24px}
h1{font-size:22px}h2{font-size:15px;color:#38bdf8;margin-top:24px}
table{border-collapse:collapse;width:100%;margin-top:8px}
th,td{padding:8px 10px;border-bottom:1px solid #22304a;text-align:left;font-size:13px}
th{color:#8fa3bf}
.badge{padding:2px 10px;border-radius:999px;font-size:11px;background:rgba(74,222,128,.15);color:#4ade80}
</style>
</head>
<body>
<h1>Model Leaderboard <span class="badge">test-set metrics</span></h1>
<h2>Temperature MAE by model (+24h) - lower is better</h2>
<svg id="chart" viewBox="0 0 700 260"></svg>
<h2>Full leaderboard</h2>
<table id="tbl"><thead><tr><th>Model</th><th>Task</th><th>Horizon</th><th>MAE</th><th>RMSE</th><th>Skill</th><th>PR-AUC</th></tr></thead><tbody></tbody></table>
<script>
const API="http://localhost:8000";
async function load(){
  const rows = await (await fetch(API+"/api/v1/models/leaderboard")).json();
  const tbody=document.querySelector("#tbl tbody");
  rows.forEach(r=>{
    const tr=document.createElement("tr");
    [r.model,r.task,r.horizon, r.mae?r.mae.toFixed(3):"-", r.rmse?r.rmse.toFixed(3):"-",
     r.skill_vs_persistence?r.skill_vs_persistence.toFixed(2):"-", r.pr_auc?r.pr_auc.toFixed(2):"-"]
     .forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.appendChild(td);});
    tbody.appendChild(tr);
  });
  const t24 = rows.filter(r=>r.task==="temperature"&&r.horizon===24&&r.mae!=null).sort((a,b)=>a.mae-b.mae);
  const svg=document.getElementById("chart");
  const W=700,H=260,pad=40;
  const max=Math.max(...t24.map(r=>r.mae),1e-9);
  const bw=(W-2*pad)/Math.max(t24.length,1)*0.6;
  t24.forEach((r,i)=>{
    const x=pad+i*((W-2*pad)/t24.length);
    const h=(r.mae/max)*(H-2*pad);
    const rect=document.createElementNS("http://www.w3.org/2000/svg","rect");
    rect.setAttribute("x",x);rect.setAttribute("y",H-pad-h);rect.setAttribute("width",bw);rect.setAttribute("height",h);
    rect.setAttribute("fill", i===0 ? "#4ade80" : "#3b82f6");
    svg.appendChild(rect);
    const t=document.createElementNS("http://www.w3.org/2000/svg","text");
    t.setAttribute("x",x);t.setAttribute("y",H-pad+14);t.setAttribute("fill","#8fa3bf");t.setAttribute("font-size","10");
    t.textContent=r.model;svg.appendChild(t);
    const v=document.createElementNS("http://www.w3.org/2000/svg","text");
    v.setAttribute("x",x);v.setAttribute("y",H-pad-h-4);v.setAttribute("fill","#e6edf7");v.setAttribute("font-size","10");
    v.textContent=r.mae.toFixed(2);svg.appendChild(v);
  });
}
load();
</script>
</body>
</html>
'''

# --- 9. India-scale parallel, chunked, resumable ingestion ---
W["src/atmosiq/ingest_india.py"] = r'''
"""Parallel, year-chunked, resumable ingestion for India-scale data.

Run:  python -m atmosiq.ingest_india
Uses a small worker pool to respect Open-Meteo rate limits, fetches one year
at a time (smaller responses, resumable), and upserts idempotently.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from atmosiq.db.repositories import LocationRepository, ObservationRepository
from atmosiq.db.session import get_session
from atmosiq.entity.config_entity import AppConfig
from atmosiq.logging.logger import logging
from atmosiq.providers import get_provider

logger = logging.getLogger("atmosiq.ingest_india")

MAX_WORKERS = 3


def year_chunks(start_year, end_year):
    for y in range(start_year, end_year + 1):
        yield f"{y}-01-01", f"{y}-12-31"


def ingest_location(session_factory, provider, location, start_year, end_year):
    total = 0
    for start, end in year_chunks(start_year, end_year):
        session = session_factory()
        try:
            bundle = provider.fetch_historical(location, start, end)
            LocationRepository(session).upsert([location])
            n = ObservationRepository(session).upsert_observations(location["id"], provider.name, bundle.hourly)
            total += n
            logger.info("chunk ok", extra={"ctx_location_id": location["id"], "ctx_range": f"{start}..{end}", "ctx_rows": n})
        except Exception as e:
            logger.error(f"chunk failed {location['id']} {start}: {e}")
        finally:
            session.close()
    return location["id"], total


def main():
    app = AppConfig()
    provider = get_provider(app.raw["provider"]["name"], app.raw["provider"])
    start_year = int(app.raw["historical"]["start_date"][:4])
    end_year = int(app.raw["historical"]["end_date"][:4])
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(ingest_location, get_session, provider, loc, start_year, end_year) for loc in app.locations]
        for fut in as_completed(futures):
            loc_id, n = fut.result()
            results[loc_id] = n
    print("Ingested rows per location:", results)
    print("Total:", sum(results.values()))


if __name__ == "__main__":
    main()
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 10 written: {len(W)} files.")