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
from atmosiq.observability.prometheus import (
    atmosiq_prediction_latency_seconds,
    atmosiq_prediction_total,
)
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

    def _get_preprocessor(self):
        import glob
        prep_files = sorted(glob.glob("artifacts/*/data_transformation/preprocessor.pkl"))
        if prep_files:
            return load_object(prep_files[-1])
        return None

    def _feature_vector(self, location_id):
        location_id = location_id or "kavali"
        if location_id in self._feature_cache:
            return self._feature_cache[location_id]
        loc = self.session.query(Location).filter_by(id=location_id).first()
        if loc is None:
            loc = self.session.query(Location).first()
        if loc is None:
            raise AtmosIQException(f"unknown location {location_id}")
        location_id = loc.id

        obs = ObservationRepository(self.session).observations_df(location_id, "open_meteo")
        if obs.empty:
            raise AtmosIQException(f"no observations for {location_id}; run ingestion first")
        obs = obs.copy()
        if "apparent_temperature" in obs.columns:
            obs["apparent_temperature"] = obs["apparent_temperature"].fillna(obs["temperature_2m"])
        prep = self._get_preprocessor()
        if prep is not None:
            try:
                from atmosiq.components.data_transformation import SCALE_COLUMNS
                scaled = prep.transform(obs[SCALE_COLUMNS])
                for i, col in enumerate(SCALE_COLUMNS):
                    obs[f"s_{col}"] = scaled[:, i]
            except Exception:
                pass
        obs["latitude"] = float(loc.latitude)
        obs["longitude"] = float(loc.longitude)
        obs["elevation"] = float(getattr(loc, "elevation", 0.0) or 0.0)
        provider = get_provider("open_meteo", {})
        forecast = provider.fetch_forecast({"id": loc.id, "latitude": loc.latitude, "longitude": loc.longitude})
        featured = build_features(obs.tail(400), forecast.hourly)
        row = featured.iloc[-1]
        self._feature_cache[location_id] = row
        return row

    def _predict_one(self, task, horizon_hours, location_id):
        try:
            version, blob = self._load_champion(task, horizon_hours)
        except AtmosIQException:
            return self._live_forecast_prediction(task, horizon_hours, location_id)
        row = self._feature_vector(location_id)
        estimator = blob["estimator"] if isinstance(blob, dict) else blob
        feature_names = getattr(estimator, "feature_names_in_", None)
        if feature_names is None or len(feature_names) == 0:
            from atmosiq.components.model_trainer import feature_columns_for
            feature_names = feature_columns_for(row.to_frame().T)
        else:
            feature_names = list(feature_names)

        vals = []
        for f in feature_names:
            v = row.get(f, 0.0)
            try:
                vals.append(float(v) if v is not None and not pd.isna(v) else 0.0)
            except (ValueError, TypeError):
                vals.append(0.0)
        X = [vals]
        raw = estimator.predict(X)[0]
        payload = {"task": task, "horizon_hours": horizon_hours, "model": version.model_name, "model_version": version.id}
        if is_classification(task):
            idx = int(raw)
            if kind_of(task) == "binary":
                proba = float(estimator.predict_proba(X)[0][1])
                opt_th = float(version.metrics.get("optimal_threshold", 0.5)) if version and version.metrics else 0.5
                payload.update({
                    "rain_probability": proba,
                    "rain_expected": bool(proba >= opt_th),
                    "optimal_threshold": opt_th,
                    "prediction": proba,
                })
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

    def _live_forecast_prediction(self, task, horizon_hours, location_id):
        from atmosiq.db.models import ModelVersion

        version = (
            self.session.query(ModelVersion)
            .filter_by(task=task, horizon_hours=horizon_hours, stage="Champion")
            .order_by(ModelVersion.created_at.desc())
            .first()
        )
        if version is None:
            raise AtmosIQException(f"No champion for task={task} horizon={horizon_hours}")

        loc = self.session.query(Location).filter_by(id=location_id or "kavali").first()
        if loc is None:
            loc = self.session.query(Location).first()
        if loc is None:
            raise AtmosIQException("no locations available for live forecast fallback")

        provider = get_provider("open_meteo", {})
        forecast = provider.fetch_forecast({"id": loc.id, "latitude": float(loc.latitude), "longitude": float(loc.longitude)})
        hourly = forecast.hourly.sort_values("lead_time_hours")
        row = hourly.loc[(hourly["lead_time_hours"] - horizon_hours).abs().idxmin()]

        source_map = {
            "temperature": "temperature_2m",
            "apparent_temperature": "apparent_temperature",
            "humidity": "relative_humidity_2m",
            "dew_point": "dew_point_2m",
            "pressure": "pressure_msl",
            "surface_pressure": "surface_pressure",
            "cloud_cover": "cloud_cover",
            "visibility": "visibility",
            "precipitation_amount": "precipitation",
            "precipitation_probability": "precipitation_probability",
            "wind_speed": "wind_speed_10m",
            "wind_gusts": "wind_gusts_10m",
            "wind_direction": "wind_direction_10m",
            "weather_condition": "weather_code",
        }
        payload = {
            "task": task,
            "horizon_hours": horizon_hours,
            "model": version.model_name,
            "model_version": version.id,
            "source": "live_open_meteo_fallback",
        }
        if task == "rain_occurrence":
            prob = float(row.get("precipitation_probability", 0.0) or 0.0) / 100.0
            payload.update({"rain_probability": prob, "rain_expected": prob >= 0.45, "optimal_threshold": 0.45, "prediction": prob})
        elif task == "weather_condition":
            code = int(row.get("weather_code", 0) or 0)
            payload.update({"condition": str(code), "prediction": code})
        elif task == "wind_direction":
            deg = float(row.get("wind_direction_10m", 0.0) or 0.0)
            idx = int(round(deg / 22.5)) % 16
            payload.update({"direction": COMPASS_16[idx], "prediction": idx})
        else:
            col = source_map.get(task)
            val = float(row.get(col, 0.0) or 0.0) if col else 0.0
            payload["prediction"] = val
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

        # Two-stage hurdle model: Calibrate precipitation amount using rain_occurrence probability
        rain_occ = t.get("rain_occurrence")
        precip_amt = t.get("precipitation_amount")
        if rain_occ and precip_amt:
            prob = rain_occ.get("rain_probability", 0.0)
            threshold = rain_occ.get("optimal_threshold", 0.45)
            if prob < threshold:
                precip_amt["prediction"] = 0.0
                precip_amt["lower"] = 0.0
                precip_amt["upper"] = round(prob * 0.5, 2)
            else:
                raw_amt = precip_amt.get("prediction", 0.0)
                precip_amt["prediction"] = round(max(0.1, raw_amt * (prob ** 0.5)), 2)

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

    def predict_timeline(self, location_id, horizons=None):
        horizons = horizons or [1, 3, 6, 12, 24, 48, 72]
        # Pre-warm feature cache once
        self._feature_vector(location_id)
        timeline = []
        for h in horizons:
            timeline.append(self.predict_full(location_id, h))
        return {"location": location_id, "horizons": horizons, "timeline": timeline}
