"""SQLAlchemy 2.x ORM. Tables created via Alembic in production."""
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

TZ = DateTime(timezone=True)


def _now():
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class WeatherObservation(Base):
    __tablename__ = "weather_observations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32))
    observation_time: Mapped[datetime] = mapped_column(TZ)
    temperature_2m: Mapped[float] = mapped_column(Float, nullable=True)
    relative_humidity_2m: Mapped[float] = mapped_column(Float, nullable=True)
    dew_point_2m: Mapped[float] = mapped_column(Float, nullable=True)
    apparent_temperature: Mapped[float] = mapped_column(Float, nullable=True)
    precipitation: Mapped[float] = mapped_column(Float, nullable=True)
    rain: Mapped[float] = mapped_column(Float, nullable=True)
    showers: Mapped[float] = mapped_column(Float, nullable=True)
    snowfall: Mapped[float] = mapped_column(Float, nullable=True)
    precipitation_probability: Mapped[float] = mapped_column(Float, nullable=True)
    pressure_msl: Mapped[float] = mapped_column(Float, nullable=True)
    surface_pressure: Mapped[float] = mapped_column(Float, nullable=True)
    cloud_cover: Mapped[float] = mapped_column(Float, nullable=True)
    visibility: Mapped[float] = mapped_column(Float, nullable=True)
    wind_speed_10m: Mapped[float] = mapped_column(Float, nullable=True)
    wind_direction_10m: Mapped[float] = mapped_column(Float, nullable=True)
    wind_gusts_10m: Mapped[float] = mapped_column(Float, nullable=True)
    weather_code: Mapped[int] = mapped_column(Integer, nullable=True)
    ingestion_time: Mapped[datetime] = mapped_column(TZ, default=_now)
    __table_args__ = (
        UniqueConstraint("location_id", "observation_time", "provider", name="uq_obs_loc_time_provider"),
        Index("ix_obs_time", "location_id", "observation_time"),
    )


class ForecastRun(Base):
    __tablename__ = "weather_forecast_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32))
    issue_time: Mapped[datetime] = mapped_column(TZ)
    request_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)
    __table_args__ = (UniqueConstraint("location_id", "provider", "issue_time", name="uq_run_loc_provider_issue"),)


class Forecast(Base):
    __tablename__ = "weather_forecasts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("weather_forecast_runs.id"))
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), index=True)
    valid_time: Mapped[datetime] = mapped_column(TZ)
    lead_time_hours: Mapped[float] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint("run_id", "location_id", "valid_time", name="uq_forecast_run_loc_valid"),)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    provider: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(TZ)
    finished_at: Mapped[datetime] = mapped_column(TZ, nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    observation_count: Mapped[int] = mapped_column(Integer, default=0)
    forecast_count: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)


class ValidationRun(Base):
    __tablename__ = "validation_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ingestion_run_id: Mapped[str] = mapped_column(ForeignKey("ingestion_runs.id"))
    status: Mapped[str] = mapped_column(String(16))
    rejected_rows: Mapped[int] = mapped_column(Integer, default=0)
    report: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_dir: Mapped[str] = mapped_column(Text)
    split_boundaries: Mapped[dict] = mapped_column(JSON)
    row_counts: Mapped[dict] = mapped_column(JSON)
    content_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class FeatureVersion(Base):
    __tablename__ = "feature_versions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    feature_columns: Mapped[dict] = mapped_column(JSON)
    config_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class TrainingRun(Base):
    __tablename__ = "training_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64))
    task: Mapped[str] = mapped_column(String(32))
    horizon_hours: Mapped[int] = mapped_column(Integer)
    dataset_version_id: Mapped[str] = mapped_column(ForeignKey("dataset_versions.id"))
    feature_version_id: Mapped[str] = mapped_column(ForeignKey("feature_versions.id"), nullable=True)
    hyperparameters: Mapped[dict] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
    git_commit: Mapped[str] = mapped_column(String(64), nullable=True)
    seed: Mapped[int] = mapped_column(Integer, default=42)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    environment: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64), index=True)
    task: Mapped[str] = mapped_column(String(32))
    horizon_hours: Mapped[int] = mapped_column(Integer)
    location_id: Mapped[str] = mapped_column(String(32), nullable=True)
    stage: Mapped[str] = mapped_column(String(16), default="Development")
    training_run_id: Mapped[str] = mapped_column(ForeignKey("training_runs.id"))
    artifact_path: Mapped[str] = mapped_column(Text)
    preprocessor_path: Mapped[str] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    issue_time: Mapped[datetime] = mapped_column(TZ)
    valid_time: Mapped[datetime] = mapped_column(TZ)
    horizon_hours: Mapped[int] = mapped_column(Integer)
    task: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class ForecastVerification(Base):
    __tablename__ = "forecast_verifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    issue_time: Mapped[datetime] = mapped_column(TZ)
    valid_time: Mapped[datetime] = mapped_column(TZ)
    lead_time_hours: Mapped[float] = mapped_column(Float)
    task: Mapped[str] = mapped_column(String(32))
    forecast_value: Mapped[float] = mapped_column(Float, nullable=True)
    actual_value: Mapped[float] = mapped_column(Float, nullable=True)
    error: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class DriftEvent(Base):
    __tablename__ = "drift_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature: Mapped[str] = mapped_column(String(64))
    reference_period: Mapped[str] = mapped_column(String(64))
    current_period: Mapped[str] = mapped_column(String(64))
    psi: Mapped[float] = mapped_column(Float, nullable=True)
    ks_statistic: Mapped[float] = mapped_column(Float, nullable=True)
    p_value: Mapped[float] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float)
    detected: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class PerformanceEvent(Base):
    __tablename__ = "performance_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    window_start: Mapped[datetime] = mapped_column(TZ)
    window_end: Mapped[datetime] = mapped_column(TZ)
    metrics: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    scope: Mapped[str] = mapped_column(String(128))
    message: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="open")
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)


class Deployment(Base):
    __tablename__ = "deployments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_version_id: Mapped[str] = mapped_column(ForeignKey("model_versions.id"))
    task: Mapped[str] = mapped_column(String(32))
    horizon_hours: Mapped[int] = mapped_column(Integer)
    location_id: Mapped[str] = mapped_column(String(32), nullable=True)
    action: Mapped[str] = mapped_column(String(16))
    actor: Mapped[str] = mapped_column(String(64), default="system")
    created_at: Mapped[datetime] = mapped_column(TZ, default=_now)
