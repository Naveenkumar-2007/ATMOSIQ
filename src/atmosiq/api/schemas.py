from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str


class LocationOut(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    timezone: str


class CurrentWeatherOut(BaseModel):
    location: str
    observation_time: str
    temperature_2m: float | None = None
    apparent_temperature: float | None = None
    relative_humidity_2m: float | None = None
    wind_speed_10m: float | None = None
    pressure_msl: float | None = None
    visibility: float | None = None
    weather_code: int | None = None


class HourlyForecastOut(BaseModel):
    location: str
    times: list[str]
    temperature_2m: list[float | None]
    precipitation: list[float | None]
    precipitation_probability: list[float | None]
    wind_speed_10m: list[float | None]


class DailyForecastOut(BaseModel):
    location: str
    dates: list[str]
    temperature_max: list[float | None]
    temperature_min: list[float | None]
    precipitation_sum: list[float | None]
    precipitation_probability_max: list[float | None]
    wind_speed_max: list[float | None]


class PredictTemperatureRequest(BaseModel):
    location: str
    horizon_hours: int = Field(default=24, ge=1, le=72)
    features: dict


class TemperaturePredictionOut(BaseModel):
    location: str
    forecast_issue_time: str
    horizon_hours: int
    model: str
    model_version: str
    prediction: float
    lower: float | None = None
    upper: float | None = None


class PredictRainRequest(BaseModel):
    location: str
    horizon_hours: int = Field(default=24, ge=1, le=72)
    features: dict


class RainPredictionOut(BaseModel):
    location: str
    forecast_issue_time: str
    horizon_hours: int
    rain_probability: float | None = None
    rainfall_mm: float | None = None
    category: str
    model: str
    model_version: str


class PredictWindRequest(BaseModel):
    location: str
    horizon_hours: int = Field(default=24, ge=1, le=72)
    features: dict


class WindPredictionOut(BaseModel):
    location: str
    forecast_issue_time: str
    horizon_hours: int
    wind_speed: float
    model: str
    model_version: str


class ModelOut(BaseModel):
    id: str
    model_name: str
    task: str
    horizon_hours: int
    stage: str
    location_id: str | None = None


class MonitoringSummaryOut(BaseModel):
    active_alerts: int
    drift_events: int
    performance_events: int
    champion_count: int


class DriftEventOut(BaseModel):
    feature: str
    reference_period: str
    current_period: str
    psi: float | None = None
    ks_statistic: float | None = None
    p_value: float | None = None
    threshold: float
    detected: bool
    timestamp: str


# ── Extended schemas for new endpoints ──────────────────────────


class ModelDetailOut(BaseModel):
    id: str
    model_name: str
    task: str
    horizon_hours: int
    stage: str
    location_id: str | None = None
    training_run_id: str
    artifact_path: str
    preprocessor_path: str | None = None
    metrics: dict | None = None
    created_at: str


class VerificationRow(BaseModel):
    id: int
    model_version_id: str
    location_id: str
    issue_time: str
    valid_time: str
    lead_time_hours: float
    task: str
    forecast_value: float | None = None
    actual_value: float | None = None
    error: float | None = None


class VerificationResponse(BaseModel):
    rows: list[VerificationRow]
    total: int
    summary: dict


class PredictionRow(BaseModel):
    id: int
    request_id: str
    model_version_id: str
    location_id: str
    issue_time: str
    valid_time: str
    horizon_hours: int
    task: str
    payload: dict


class PredictionHistoryResponse(BaseModel):
    rows: list[PredictionRow]
    total: int


class TrainingRunOut(BaseModel):
    id: str
    model_name: str
    task: str
    horizon_hours: int
    metrics: dict | None = None
    hyperparameters: dict | None = None
    seed: int = 42
    duration_seconds: float | None = None
    dataset_version_id: str | None = None
    feature_version_id: str | None = None
    git_commit: str | None = None
    environment: dict | None = None
    created_at: str


class ServiceStatus(BaseModel):
    name: str
    status: str  # healthy | degraded | down
    latency_ms: float | None = None
    details: str | None = None


class SystemHealthOut(BaseModel):
    status: str  # healthy | degraded | down
    version: str
    services: list[ServiceStatus]
    last_ingestion: str | None = None
    last_prediction: str | None = None
    last_training: str | None = None
    model_count: int = 0
    champion_count: int = 0
    observation_count: int = 0
    prediction_count: int = 0


class ModelMonitoringOut(BaseModel):
    prediction_volume_24h: int
    prediction_volume_7d: int
    avg_latency_ms: float | None = None
    error_rate: float = 0.0
    active_models: int = 0
    champion_models: int = 0
    drift_events_30d: int = 0
    performance_events_30d: int = 0
