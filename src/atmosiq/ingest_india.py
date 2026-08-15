import time
from atmosiq.common.timeutils import resolve_date
from atmosiq.db.repositories import LocationRepository, ObservationRepository
from atmosiq.db.session import get_session
from atmosiq.db.models import WeatherObservation
from atmosiq.entity.config_entity import AppConfig
from atmosiq.logging.logger import logging
from atmosiq.providers import get_provider

logger = logging.getLogger("atmosiq.ingest_india")


def ingest_location(provider, location, start_date, end_date):
    session = get_session()
    try:
        # Check existing count in DB to make it smart & resumable
        existing = session.query(WeatherObservation).filter_by(location_id=location["id"]).count()
        if existing >= 17000:
            logger.info("location already ingested, skipping", extra={"ctx_location_id": location["id"], "ctx_existing": existing})
            return location["id"], existing

        logger.info("fetching location", extra={"ctx_location_id": location["id"], "ctx_range": f"{start_date}..{end_date}"})
        bundle = provider.fetch_historical(location, start_date, end_date)
        LocationRepository(session).upsert([location])
        n = ObservationRepository(session).upsert_observations(location["id"], provider.name, bundle.hourly)
        logger.info("ingest ok", extra={"ctx_location_id": location["id"], "ctx_rows": n})
        time.sleep(2.0)
        return location["id"], n
    except Exception as e:
        logger.error(f"ingest failed for {location['id']}: {e}")
        return location["id"], 0
    finally:
        session.close()


def main():
    app = AppConfig()
    provider = get_provider(app.raw["provider"]["name"], app.raw["provider"])
    start_date = resolve_date(app.raw["historical"]["start_date"])
    end_date = resolve_date(app.raw["historical"]["end_date"])
    results = {}
    
    print(f"Starting polite sequential ingestion for {len(app.locations)} locations ({start_date} to {end_date})...")
    for loc in app.locations:
        loc_id, n = ingest_location(provider, loc, start_date, end_date)
        results[loc_id] = n

    print("\n--- Ingestion Summary ---")
    print("Rows per location:", results)
    print("Total rows:", sum(results.values()))


if __name__ == "__main__":
    main()
