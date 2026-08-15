from atmosiq.components.alert_manager import AlertManager
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.logging.logger import logging
from atmosiq.pipeline.training_pipeline import TrainingPipeline

logger = logging.getLogger("atmosiq.components.retraining_service")


class RetrainingService:
    def __init__(self, session, drift_threshold_events=2):
        self.session = session
        self.repo = MonitoringRepository(session)
        self.drift_threshold_events = drift_threshold_events
        self.alerts = AlertManager(session)

    def should_retrain(self, drift_events_recent, performance_degraded):
        confirmed_drift = len([e for e in drift_events_recent if e.detected]) >= self.drift_threshold_events
        if confirmed_drift and performance_degraded:
            return True, "drift+degradation"
        if performance_degraded:
            return True, "performance_degradation"
        if confirmed_drift:
            return True, "confirmed_drift"
        return False, "no_trigger"

    def run_retraining(self, trigger_reason, approved_by=None):
        logger.info("retraining triggered", extra={"ctx_reason": trigger_reason})
        pipeline = TrainingPipeline(session=self.session, approved_by=approved_by, deep=False, tune=False)
        artifacts = pipeline.run()
        pusher = artifacts["pusher"]
        if pusher.stage == "Champion":
            logger.info("retraining promoted champion", extra={"ctx_version": pusher.model_version_id})
        else:
            logger.info("retraining candidate not promoted", extra={"ctx_stage": pusher.stage})
        return {"trigger_reason": trigger_reason, "pusher": pusher}
