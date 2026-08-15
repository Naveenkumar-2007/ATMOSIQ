import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from atmosiq.db.models import Location, WeatherObservation


def test_duplicate_observation_rejected(sqlite_session):
    sqlite_session.add(Location(id="test", name="Test", latitude=15.0, longitude=80.0, timezone="UTC"))
    sqlite_session.commit()
    t = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
    sqlite_session.add(WeatherObservation(location_id="test", provider="open_meteo", observation_time=t, temperature_2m=20.0))
    sqlite_session.commit()
    sqlite_session.add(WeatherObservation(location_id="test", provider="open_meteo", observation_time=t, temperature_2m=21.0))
    with pytest.raises(IntegrityError):
        sqlite_session.commit()
    sqlite_session.rollback()
    assert sqlite_session.query(WeatherObservation).count() == 1
