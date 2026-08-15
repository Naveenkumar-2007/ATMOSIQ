import numpy as np
import pandas as pd

from atmosiq.db.models import PerformanceEvent
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_model_health, atmosiq_model_performance
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.performance_monitor")


class PerformanceMonitor:
    def __init__(self, session):
        self.session = session
        self.repo = MonitoringRepository(session)

    def rolling_metrics(self, predictions, window_hours=168):
        if predictions.empty or "valid_time" not in predictions.columns:
            return {}
        df = predictions.sort_values("valid_time").set_index("valid_time")
        recent = df.last(f"{window_hours}h")
        if recent.empty or "actual_value" not in recent.columns or recent["actual_value"].isna().all():
            return {}
        y = recent["actual_value"].to_numpy()
        p = recent["forecast_value"].to_numpy()
        return {"mae": metric.mae(y, p), "rmse": metric.rmse(y, p), "bias": float(np.mean(p - y)), "window_hours": window_hours, "n": int(len(recent))}

    def verify_by_horizon(self, verifications):
        if not verifications:
            return {}
        records = [
            {
                "lead_time_hours": v.lead_time_hours,
                "error": v.error if v.error is not None else (v.forecast_value - v.actual_value if v.forecast_value is not None and v.actual_value is not None else None),
            }
            for v in verifications
        ]
        df = pd.DataFrame(records)
        if df.empty or "error" not in df.columns:
            return {}
        df = df.dropna(subset=["error"])
        if df.empty:
            return {}
        buckets = [(0, 2), (2, 12), (12, 30), (30, 54), (54, 120)]
        result = {}
        for low, high in buckets:
            sub = df[(df["lead_time_hours"] > low) & (df["lead_time_hours"] <= high)]
            if sub.empty:
                continue
            label = f"{int(np.median(sub['lead_time_hours']))}h"
            result[label] = {
                "mae": float(sub["error"].abs().mean()),
                "rmse": float(np.sqrt((sub["error"] ** 2).mean())),
                "bias": float(sub["error"].mean()),
                "n": int(len(sub)),
            }
        return result

    def record_performance(self, model_version_id, metrics, window_start, window_end):
        self.repo.add_performance_event(PerformanceEvent(model_version_id=model_version_id, window_start=window_start, window_end=window_end, metrics=metrics))
        if "mae" in metrics:
            atmosiq_model_performance.labels(model=model_version_id, task="temperature", metric="mae").set(metrics["mae"])

    def assess_health(self, current_metrics, baseline_mae, tolerance=1.5):
        if not current_metrics or "mae" not in current_metrics:
            return False
        healthy = current_metrics["mae"] <= baseline_mae * tolerance
        atmosiq_model_health.labels(model="champion", task="temperature").set(1.0 if healthy else 0.0)
        return healthy
