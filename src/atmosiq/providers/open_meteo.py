import pandas as pd

from atmosiq.common.timeutils import floor_hour, lead_time_hours, now_utc
from atmosiq.constant.training_pipeline import (
    DAILY_CANONICAL,
    DAILY_HISTORICAL_VARIABLES,
    DAILY_VARIABLES,
    HISTORICAL_HOURLY_VARIABLES,
    HOURLY_VARIABLES,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.providers.base import ForecastBundle, HistoricalBundle, ProviderMeta, WeatherProvider

logger = logging.getLogger("atmosiq.providers.open_meteo")

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Archive daily names -> canonical names (so downstream code is uniform).
ARCHIVE_DAILY_RENAME = {
    "temperature_2m_max": "temperature_max",
    "temperature_2m_min": "temperature_min",
    "wind_speed_10m_max": "wind_speed_max",
    "wind_gusts_10m_max": "wind_gusts_max",
    # precipitation_sum keeps its name
}
class OpenMeteoProvider(WeatherProvider):
    name = "open_meteo"

    def _params(self, location, hourly_vars, daily_vars):
        return {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "hourly": ",".join(hourly_vars),
            "daily": ",".join(daily_vars),
            "timezone": "UTC",
        }

    def _normalize_hourly(self, payload, expected_vars, meta):
        hourly = payload.get("hourly")
        if not hourly or "time" not in hourly:
            raise AtmosIQException(f"Open-Meteo response missing hourly block (request {meta.request_id})")
        times = pd.to_datetime(hourly["time"], utc=True)
        df = pd.DataFrame({"time": times})
        for var in expected_vars:
            if var in hourly:
                df[var] = pd.to_numeric(pd.Series(hourly[var]), errors="coerce")
            else:
                df[var] = float("nan")
        for var in HOURLY_VARIABLES:
            if var not in df.columns:
                df[var] = float("nan")
        if "weather_code" in df.columns:
            df["weather_code"] = df["weather_code"].astype("Int64")
        return df

    def _normalize_daily_archive(self, payload):
        daily = payload.get("daily", {})
        if not daily or "time" not in daily:
            return pd.DataFrame()
        df = pd.DataFrame({"date": pd.to_datetime(daily["time"], utc=True)})
        for var in DAILY_HISTORICAL_VARIABLES:
            if var in daily:
                df[var] = pd.to_numeric(pd.Series(daily[var]), errors="coerce")
            else:
                df[var] = float("nan")
        df = df.rename(columns=ARCHIVE_DAILY_RENAME)
        for col in DAILY_CANONICAL:
            if col not in df.columns:
                df[col] = float("nan")
        return df

    def _normalize_daily_forecast(self, payload):
        daily = payload.get("daily", {})
        if not daily or "time" not in daily:
            return pd.DataFrame()
        df = pd.DataFrame({"date": pd.to_datetime(daily["time"], utc=True)})
        for var in DAILY_VARIABLES:
            if var in daily:
                df[var] = pd.to_numeric(pd.Series(daily[var]), errors="coerce")
            else:
                df[var] = float("nan")
        df = df.rename(columns=ARCHIVE_DAILY_RENAME)
        return df

    def fetch_historical(self, location, start_date, end_date):
        import httpx
        meta = ProviderMeta(provider=self.name, fetched_at=now_utc())
        params = self._params(location, HISTORICAL_HOURLY_VARIABLES, DAILY_HISTORICAL_VARIABLES)
        params.update({"start_date": start_date, "end_date": end_date})
        with httpx.Client() as client:
            raw = self._request_json(client, ARCHIVE_URL, params, meta)
        hourly = self._normalize_hourly(raw, HISTORICAL_HOURLY_VARIABLES, meta)
        daily = self._normalize_daily_archive(raw)
        logger.info("historical fetch ok", extra={"ctx_location_id": location["id"], "ctx_rows": len(hourly)})
        return HistoricalBundle(location["id"], hourly, daily, raw, meta)

    def fetch_forecast(self, location):
        import httpx
        meta = ProviderMeta(provider=self.name, fetched_at=now_utc())
        params = self._params(location, HOURLY_VARIABLES, DAILY_VARIABLES)
        params.update({"forecast_days": 4, "forecast_hours": 96})
        with httpx.Client() as client:
            raw = self._request_json(client, FORECAST_URL, params, meta)
        hourly = self._normalize_hourly(raw, HOURLY_VARIABLES, meta)
        daily = self._normalize_daily_forecast(raw)
        issue_time = floor_hour(now_utc())
        hourly["issue_time"] = issue_time
        hourly["valid_time"] = hourly["time"]
        hourly["lead_time_hours"] = hourly["valid_time"].map(
            lambda vt: lead_time_hours(issue_time, vt.to_pydatetime() if hasattr(vt, "to_pydatetime") else vt)
        )
        logger.info("forecast fetch ok", extra={"ctx_location_id": location["id"]})
        return ForecastBundle(location["id"], issue_time, hourly, daily, raw, meta)
