import numpy as np
from scipy.stats import ks_2samp

from atmosiq.common.timeutils import now_utc
from atmosiq.db.models import DriftEvent
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_data_drift_events_total
from atmosiq.utils.main_utils.utils import write_json_file

logger = logging.getLogger("atmosiq.components.drift_monitor")


def compute_psi(reference, current, bins=10):
    reference = reference[~np.isnan(reference)]
    current = current[~np.isnan(current)]
    if len(reference) < 2 or len(current) < 2:
        return float("nan")
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    eps = 1e-6
    ref_frac = (ref_counts + eps) / (ref_counts.sum() + eps * bins)
    cur_frac = (cur_counts + eps) / (cur_counts.sum() + eps * bins)
    return float(np.sum((cur_frac - ref_frac) * np.log(cur_frac / ref_frac)))


class DriftMonitor:
    def __init__(self, session, psi_threshold=0.25, ks_alpha=0.05):
        self.session = session
        self.repo = MonitoringRepository(session)
        self.psi_threshold = psi_threshold
        self.ks_alpha = ks_alpha

    def check_feature(self, feature, reference, current, reference_period, current_period):
        psi = compute_psi(reference, current)
        ks_res = ks_2samp(reference, current)
        ks_stat = float(ks_res.statistic)
        p_value = float(ks_res.pvalue)
        psi_val = float(psi) if not np.isnan(psi) else 0.0
        detected = bool(psi_val > self.psi_threshold) or bool(p_value < self.ks_alpha)
        event = DriftEvent(
            feature=feature, reference_period=reference_period, current_period=current_period,
            psi=psi_val, ks_statistic=ks_stat, p_value=p_value, threshold=float(self.psi_threshold), detected=detected,
        )
        self.repo.add_drift_event(event)
        if detected:
            atmosiq_data_drift_events_total.labels(feature=feature).inc()
            logger.warning("drift detected", extra={"ctx_feature": feature, "ctx_psi": round(psi, 4)})
        return event

    def check_dataframe(self, reference_df, current_df, feature_columns):
        events = []
        reference_period = f"{reference_df['time'].min()}__{reference_df['time'].max()}" if "time" in reference_df else "reference"
        current_period = f"{current_df['time'].min()}__{current_df['time'].max()}" if "time" in current_df else "current"
        for column in feature_columns:
            if column not in reference_df.columns or column not in current_df.columns:
                continue
            events.append(self.check_feature(
                column,
                reference_df[column].to_numpy(dtype=float),
                current_df[column].to_numpy(dtype=float),
                reference_period,
                current_period,
            ))
        return events

    def write_report(self, events, path):
        payload = [
            {
                "feature": e.feature, "psi": e.psi, "ks_statistic": e.ks_statistic, "p_value": e.p_value,
                "threshold": e.threshold, "detected": e.detected,
                "reference_period": e.reference_period, "current_period": e.current_period,
            }
            for e in events
        ]
        write_json_file(path, {"generated_at": now_utc().isoformat(), "events": payload})
