import os
import sys
import uuid

from atmosiq.common.timeutils import now_utc, resolve_date
from atmosiq.db.models import IngestionRun
from atmosiq.db.repositories import (
    ForecastRepository,
    LocationRepository,
    ObservationRepository,
    RunRepository,
)
from atmosiq.entity.artifact_entity import DataIngestionArtifact
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.data_ingestion")


class DataIngestion:
    def __init__(self, data_ingestion_config, provider, session=None):
        try:
            self.config = data_ingestion_config
            self.provider = provider
            self.session = session
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _ingest_location(self, location):
        start = resolve_date(self.config.app.raw["historical"]["start_date"])
        end = resolve_date(self.config.app.raw["historical"]["end_date"])
        obs_count = 0
        fc_count = 0
        hourly_df = None
        daily_df = None

        if self.session is not None:
            LocationRepository(self.session).upsert([location])
            existing_obs = ObservationRepository(self.session).observations_df(location["id"], self.provider.name)
            if not existing_obs.empty and len(existing_obs) >= 1000:
                hourly_df = existing_obs
                obs_count = len(existing_obs)
                logger.info(f"using {obs_count} stored PostgreSQL observations for {location['id']}")

        if hourly_df is None:
            try:
                historical = self.provider.fetch_historical(location, start, end)
                write_json_file(os.path.join(self.config.raw_dir, f"{location['id']}_historical_raw.json"), historical.raw)
                hourly_df = historical.hourly
                daily_df = historical.daily
                if self.session is not None:
                    obs_count = ObservationRepository(self.session).upsert_observations(location["id"], self.provider.name, historical.hourly)
            except Exception as e:
                logger.warning(f"fetch skipped for {location['id']}: {e}")

        if self.session is not None:
            try:
                forecast = self.provider.fetch_forecast(location)
                save_parquet(forecast.hourly, os.path.join(self.config.forecast_dir, f"{location['id']}_forecast.parquet"))
                write_json_file(os.path.join(self.config.forecast_dir, f"{location['id']}_forecast_raw.json"), forecast.raw)
                fc_count = ForecastRepository(self.session).store_forecast_run(location["id"], self.provider.name, forecast.issue_time, forecast.meta.request_id, forecast.hourly)
            except Exception:
                pass

        if hourly_df is not None and not hourly_df.empty:
            bronze = hourly_df.copy()
            bronze["latitude"] = float(location["latitude"])
            bronze["longitude"] = float(location["longitude"])
            save_parquet(bronze, os.path.join(self.config.bronze_dir, f"{location['id']}_hourly.parquet"))
        if daily_df is not None and not daily_df.empty:
            save_parquet(daily_df, os.path.join(self.config.bronze_dir, f"{location['id']}_daily.parquet"))
        return obs_count, fc_count

    def initiate_data_ingestion(self):
        try:
            run_id = f"ing_{uuid.uuid4().hex[:12]}"
            total_obs = 0
            total_fc = 0
            locations_to_ingest = list(self.config.app.locations)
            if self.session is not None:
                from atmosiq.db.models import Location
                db_locs = self.session.query(Location).all()
                existing_ids = {l["id"] for l in locations_to_ingest}
                for dbl in db_locs:
                    if dbl.id not in existing_ids:
                        locations_to_ingest.append({
                            "id": dbl.id,
                            "name": dbl.name,
                            "latitude": float(dbl.latitude),
                            "longitude": float(dbl.longitude),
                            "elevation": float(getattr(dbl, "elevation", 0.0) or 0.0),
                            "timezone": dbl.timezone or "Asia/Kolkata",
                        })

            for location in locations_to_ingest:
                obs, fc = self._ingest_location(location)
                total_obs += obs
                total_fc += fc

            if self.session is not None:
                first_loc = locations_to_ingest[0]["id"] if locations_to_ingest else "global"
                RunRepository(self.session).add_ingestion_run(IngestionRun(
                    id=run_id, location_id=first_loc, provider=self.provider.name,
                    started_at=now_utc(), finished_at=now_utc(), status="success",
                    observation_count=total_obs, forecast_count=total_fc, meta={"locations": len(locations_to_ingest)},
                ))
            return DataIngestionArtifact(
                raw_dir=self.config.raw_dir, bronze_dir=self.config.bronze_dir, forecast_dir=self.config.forecast_dir,
                ingestion_run_id=run_id, observation_count=total_obs, forecast_count=total_fc,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
