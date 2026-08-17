import os
import time

from atmosiq.db.session import get_session
from atmosiq.logging.logger import logging
from atmosiq.pipeline.monitoring_pipeline import MonitoringPipeline
from atmosiq.components.production_mloops import retraining_status, run_lightweight_retraining

logger = logging.getLogger("atmosiq.worker")

MONITOR_INTERVAL_SECONDS = int(os.getenv("MONITOR_INTERVAL_SECONDS", "300"))
RETRAIN_INTERVAL_SECONDS = int(os.getenv("RETRAIN_INTERVAL_SECONDS", "86400"))
RETRAIN_MODE = os.getenv("MLOPS_RETRAIN_MODE", "lightweight").lower()


def main():
    session = get_session()
    last_monitor = 0.0
    logger.info("worker started", extra={"ctx_retrain_mode": RETRAIN_MODE})
    while True:
        now = time.monotonic()
        if now - last_monitor >= MONITOR_INTERVAL_SECONDS:
            try:
                result = MonitoringPipeline(session).run_cycle()
                logger.info("monitoring cycle", extra={"ctx_result": result})
            except Exception as e:
                logger.error(f"monitoring cycle failed: {e}")
            last_monitor = now
        status = retraining_status(session, RETRAIN_INTERVAL_SECONDS)
        if status["due"]:
            try:
                if RETRAIN_MODE == "full":
                    from atmosiq.components.retraining_service import RetrainingService
                    RetrainingService(session).run_retraining("scheduled")
                else:
                    result = run_lightweight_retraining(session, "scheduled")
                    logger.info("lightweight retraining result", extra={"ctx_result": result})
            except Exception as e:
                logger.error(f"retraining failed: {e}")
        time.sleep(10)


if __name__ == "__main__":
    main()
