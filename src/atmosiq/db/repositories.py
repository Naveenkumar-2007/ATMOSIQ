"""Repositories: the only place ORM writes happen. No SQL in API routes."""
from sqlalchemy import select
from sqlalchemy.dialects import postgresql, sqlite

from atmosiq.db.models import (
    Alert,
    DriftEvent,
    Forecast,
    ForecastRun,
    Location,
    ModelVersion,
    WeatherObservation,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging

logger = logging.getLogger("atmosiq.db.repositories")


def _on_conflict_do_nothing(session, model, rows, batch_size=500):
    if not rows:
        return 0
    dialect = session.get_bind().dialect.name
    stmt_cls = postgresql.insert if dialect == "postgresql" else sqlite.insert
    cols = None
    for table_arg in getattr(model, "__table_args__", ()):
        if getattr(table_arg, "name", "") and table_arg.name.startswith("uq_"):
            cols = [col.name for col in table_arg.columns]
            break
    total = len(rows)
    for i in range(0, total, batch_size):
        chunk = rows[i:i + batch_size]
        stmt = stmt_cls(model).values(chunk)
        if cols:
            stmt = stmt.on_conflict_do_nothing(index_elements=cols)
        session.execute(stmt)
    return total


class LocationRepository:
    def __init__(self, session):
        self.session = session

    def upsert(self, locations):
        for loc in locations:
            if self.session.get(Location, loc["id"]) is None:
                self.session.add(Location(**loc))
        self.session.commit()


class ObservationRepository:
    def __init__(self, session):
        self.session = session

    def upsert_observations(self, location_id, provider, df):
        rows = []
        for record in df.to_dict("records"):
            row = {k: (None if _isna(v) else v) for k, v in record.items() if k != "time"}
            row["location_id"] = location_id
            row["provider"] = provider
            row["observation_time"] = record["time"].to_pydatetime()
            rows.append(row)
        inserted = _on_conflict_do_nothing(self.session, WeatherObservation, rows)
        self.session.commit()
        return inserted

    def latest_observation_time(self, location_id, provider):
        stmt = (
            select(WeatherObservation.observation_time)
            .where(WeatherObservation.location_id == location_id)
            .where(WeatherObservation.provider == provider)
            .order_by(WeatherObservation.observation_time.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def observations_df(self, location_id, provider):
        import pandas as pd
        stmt = (
            select(WeatherObservation)
            .where(WeatherObservation.location_id == location_id)
            .where(WeatherObservation.provider == provider)
            .order_by(WeatherObservation.observation_time)
        )
        objs = self.session.execute(stmt).scalars().all()
        df = pd.DataFrame([
            {c.name: getattr(o, c.name) for c in WeatherObservation.__table__.columns if c.name not in ("id", "ingestion_time")}
            for o in objs
        ])
        if not df.empty:
            df = df.rename(columns={"observation_time": "time"})
            df["time"] = _to_utc(df["time"])
        return df


def _isna(v):
    import pandas as pd
    try:
        return pd.isna(v)
    except (ValueError, TypeError):
        return False


def _to_utc(series):
    import pandas as pd
    s = pd.to_datetime(series, utc=True)
    return s


class ForecastRepository:
    def __init__(self, session):
        self.session = session

    def store_forecast_run(self, location_id, provider, issue_time, request_id, df):
        stmt = (
            select(ForecastRun)
            .where(
                ForecastRun.location_id == location_id,
                ForecastRun.provider == provider,
                ForecastRun.issue_time == issue_time,
            )
        )
        run = self.session.execute(stmt).scalar_one_or_none()
        if run is None:
            run = ForecastRun(location_id=location_id, provider=provider, issue_time=issue_time, request_id=request_id)
            self.session.add(run)
            self.session.flush()
        else:
            run.request_id = request_id
            self.session.flush()

        rows = []
        for record in df.to_dict("records"):
            payload = {
                k: (None if _isna(v) else (v.isoformat() if hasattr(v, "isoformat") else v))
                for k, v in record.items()
                if k not in ("time", "issue_time", "valid_time", "lead_time_hours")
            }
            rows.append({
                "run_id": run.id,
                "location_id": location_id,
                "valid_time": record["valid_time"].to_pydatetime(),
                "lead_time_hours": float(record["lead_time_hours"]),
                "payload": payload,
            })
        _on_conflict_do_nothing(self.session, Forecast, rows)
        self.session.commit()
        return len(rows)


class RunRepository:
    def __init__(self, session):
        self.session = session

    def add_ingestion_run(self, run):
        self.session.add(run)
        self.session.commit()

    def add_validation_run(self, run):
        self.session.add(run)
        self.session.commit()

    def add_training_run(self, run):
        self.session.add(run)
        self.session.commit()


class ModelRegistryRepository:
    def __init__(self, session):
        self.session = session

    def add_version(self, version):
        self.session.add(version)
        self.session.commit()

    def champion(self, task, horizon_hours, location_id=None):
        stmt = (
            select(ModelVersion)
            .where(ModelVersion.task == task, ModelVersion.horizon_hours == horizon_hours, ModelVersion.stage == "Champion")
            .order_by(ModelVersion.created_at.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def set_stage(self, version_id, stage):
        version = self.session.get(ModelVersion, version_id)
        if version is None:
            raise AtmosIQException(f"ModelVersion {version_id} not found")
        version.stage = stage
        self.session.commit()

    def add_deployment(self, deployment):
        self.session.add(deployment)
        self.session.commit()


class MonitoringRepository:
    def __init__(self, session):
        self.session = session

    def add_drift_event(self, event):
        self.session.add(event)
        self.session.commit()

    def recent_drift(self, feature, since):
        stmt = select(DriftEvent).where(DriftEvent.feature == feature, DriftEvent.created_at >= since, DriftEvent.detected.is_(True))
        return list(self.session.execute(stmt).scalars().all())

    def add_performance_event(self, event):
        self.session.add(event)
        self.session.commit()

    def add_alert(self, alert):
        self.session.add(alert)
        self.session.commit()

    def latest_alert(self, alert_type, scope):
        stmt = select(Alert).where(Alert.alert_type == alert_type, Alert.scope == scope).order_by(Alert.created_at.desc()).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()

    def add_prediction(self, prediction):
        self.session.add(prediction)
        self.session.commit()

    def add_verification(self, verification):
        self.session.add(verification)
        self.session.commit()
