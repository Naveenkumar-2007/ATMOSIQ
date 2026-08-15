import os
import time

from atmosiq.db.session import get_session
from atmosiq.logging.logger import logging
from atmosiq.pipeline.monitoring_pipeline import MonitoringPipeline

logger = logging.getLogger("atmosiq.worker")

MONITOR_INTERVAL_SECONDS = int(os.getenv("MONITOR_INTERVAL_SECONDS", "300"))
RETRAIN_INTERVAL_SECONDS = int(os.getenv("RETRAIN_INTERVAL_SECONDS", "86400"))


def main():
    session = get_session()
    last_monitor = 0.0
    last_retrain = 0.0
    logger.info("worker started")
    while True:
        now = time.monotonic()
        if now - last_monitor >= MONITOR_INTERVAL_SECONDS:
            try:
                result = MonitoringPipeline(session).run_cycle()
                logger.info("monitoring cycle", extra={"ctx_result": result})
            except Exception as e:
                logger.error(f"monitoring cycle failed: {e}")
            last_monitor = now
        if now - last_retrain >= RETRAIN_INTERVAL_SECONDS:
            try:
                from atmosiq.components.retraining_service import RetrainingService
                RetrainingService(session).run_retraining("scheduled")
            except Exception as e:
                logger.error(f"retraining failed: {e}")
            last_retrain = now
        time.sleep(10)


if __name__ == "__main__":
    main()
