from datetime import timedelta

from atmosiq.common.timeutils import now_utc
from atmosiq.db.models import Alert
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_alerts_active

logger = logging.getLogger("atmosiq.components.alert_manager")

SEVERITY_ORDER = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}


class AlertManager:
    def __init__(self, session, cooldown_minutes=30):
        self.session = session
        self.repo = MonitoringRepository(session)
        self.cooldown = timedelta(minutes=cooldown_minutes)

    def _in_cooldown(self, alert_type, scope):
        latest = self.repo.latest_alert(alert_type, scope)
        if latest is None:
            return False
        last = latest.created_at
        if last.tzinfo is None:
            from datetime import timezone
            last = last.replace(tzinfo=timezone.utc)
        return (now_utc() - last) < self.cooldown

    def raise_alert(self, alert_type, severity, scope, message, recommendation=None):
        if severity not in SEVERITY_ORDER:
            raise AtmosIQException(f"invalid severity {severity}")
        if self._in_cooldown(alert_type, scope):
            logger.info("alert suppressed by cooldown", extra={"ctx_type": alert_type})
            return None
        alert = Alert(alert_type=alert_type, severity=severity, scope=scope, message=message, recommendation=recommendation, status="open")
        self.repo.add_alert(alert)
        atmosiq_alerts_active.labels(severity=severity, alert_type=alert_type).inc()
        logger.warning("alert raised", extra={"ctx_type": alert_type, "ctx_severity": severity})
        return alert

    def resolve_alert(self, alert_id):
        alert = self.session.get(Alert, alert_id)
        if alert is None:
            raise AtmosIQException(f"alert {alert_id} not found")
        alert.status = "resolved"
        self.session.commit()
        atmosiq_alerts_active.labels(severity=alert.severity, alert_type=alert.alert_type).dec()

    def alert_provider_failure(self, provider):
        return self.raise_alert("provider_failure", "CRITICAL", f"provider:{provider}", f"Weather provider {provider} failed", "Switch provider or retry later")

    def alert_stale_data(self, location_id, hours):
        return self.raise_alert("data_stale", "WARNING", f"location:{location_id}", f"Data for {location_id} is {hours:.1f}h stale", "Trigger ingestion")

    def alert_drift(self, feature):
        return self.raise_alert("drift_detected", "WARNING", f"feature:{feature}", f"Drift detected on {feature}", "Run retraining pipeline")

    def alert_model_degradation(self, model_version_id, mae, baseline):
        return self.raise_alert("model_degradation", "CRITICAL", f"model:{model_version_id}", f"MAE {mae:.3f} exceeds baseline {baseline:.3f}", "Rollback to previous champion")
