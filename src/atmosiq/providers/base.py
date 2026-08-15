import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging

logger = logging.getLogger("atmosiq.providers")


@dataclass
class ProviderMeta:
    provider: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fetched_at: object = None
    http_status: int = None
    retries: int = 0
    latency_seconds: float = 0.0


@dataclass
class HistoricalBundle:
    location_id: str
    hourly: object
    daily: object
    raw: dict
    meta: ProviderMeta


@dataclass
class ForecastBundle:
    location_id: str
    issue_time: object
    hourly: object
    daily: object
    raw: dict
    meta: ProviderMeta


class WeatherProvider(ABC):
    name = "abstract"

    def __init__(self, settings):
        self.settings = settings
        self.timeout = float(settings.get("timeout_seconds", 30))
        self.max_retries = int(settings.get("max_retries", 4))
        self.backoff_base = float(settings.get("backoff_base_seconds", 2.0))

    def _request_json(self, client, url, params, meta):
        import httpx
        delay = self.backoff_base
        last_error = None
        for attempt in range(self.max_retries + 3):
            try:
                started = time.monotonic()
                response = client.get(url, params=params, timeout=self.timeout)
                meta.latency_seconds = round(time.monotonic() - started, 3)
                meta.http_status = response.status_code
                if response.status_code == 429:
                    try:
                        retry_after = float(response.headers.get("Retry-After", delay))
                    except (ValueError, TypeError):
                        retry_after = delay
                    retry_after = max(retry_after, delay, 3.0)
                    logger.warning("provider rate limited", extra={"ctx_retry_after": retry_after})
                    time.sleep(retry_after)
                    delay = min(delay * 2, 30.0)
                    meta.retries += 1
                    continue
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                last_error = e
                meta.retries += 1
                if attempt < self.max_retries + 2:
                    time.sleep(delay)
                    delay = min(delay * 2, 30.0)
        raise AtmosIQException(f"Provider {self.name} request failed: {last_error}")

    @abstractmethod
    def fetch_historical(self, location, start_date, end_date):
        ...

    @abstractmethod
    def fetch_forecast(self, location):
        ...
