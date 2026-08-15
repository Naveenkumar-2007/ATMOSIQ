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
