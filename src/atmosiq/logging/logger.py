"""Structured JSON logging; components import `logging` from here."""
import logging
import os
import sys
from datetime import datetime, timezone

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = f"{datetime.now(timezone.utc).strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

_REDACT = {"password", "api_key", "token", "secret", "authorization"}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        import json
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in _REDACT:
                continue
            if key.startswith("ctx_"):
                payload[key[4:]] = value
        return json.dumps(payload, default=str)


_hf = logging.FileHandler(LOG_FILE_PATH)
_hf.setFormatter(JsonFormatter())
_hc = logging.StreamHandler(sys.stdout)
_hc.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[_hf, _hc])


def get_logger(name):
    return logging.getLogger(name)


def log_event(logger, level, event, **fields):
    logger.log(level, event, **{f"ctx_{k}": v for k, v in fields.items()})
