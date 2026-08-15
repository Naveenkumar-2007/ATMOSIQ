import os

PIPELINE_NAME: str = "AtmosIQ"
ARTIFACT_DIR: str = "artifacts"
CONFIG_FILE_PATH: str = os.path.join("config", "atmosiq.yaml")
SCHEMA_FILE_PATH: str = os.path.join("data_schema", "weather_schema.yaml")

TARGET_COLUMN = "temperature_2m"
TRAIN_FILE_NAME: str = "train.parquet"
VALIDATION_FILE_NAME: str = "validation.parquet"
TEST_FILE_NAME: str = "test.parquet"
PREPROCESSING_OBJECT_FILE_NAME: str = "preprocessor.pkl"
FEATURE_METADATA_FILE_NAME: str = "feature_metadata.json"
MODEL_FILE_NAME: str = "model.pkl"

HORIZONS: list = [1, 3, 6, 12, 24, 48, 72]

# Archive-safe (ERA5) minimal set - these are universally available in Open-Meteo archive.
HISTORICAL_HOURLY_VARIABLES: list = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m",
    "precipitation", "rain", "snowfall",
    "pressure_msl", "surface_pressure", "cloud_cover",
    "wind_speed_10m", "wind_gusts_10m",
]

# Forecast endpoint supports the full set.
HOURLY_VARIABLES: list = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
    "precipitation", "rain", "showers", "snowfall", "precipitation_probability",
    "pressure_msl", "surface_pressure", "cloud_cover", "visibility",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "weather_code",
]

DAILY_VARIABLES: list = [
    "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
    "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max",
]

DAILY_HISTORICAL_VARIABLES: list = [
    "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
    "wind_speed_10m_max", "wind_gusts_10m_max",
]

# Canonical column names (after fetch, archive columns are renamed to these).
DAILY_CANONICAL: list = [
    "temperature_max", "temperature_min", "precipitation_sum",
    "wind_speed_max", "wind_gusts_max",
]

DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_RAW_DIR: str = "raw"
DATA_INGESTION_BRONZE_DIR: str = "bronze"
DATA_INGESTION_FORECAST_DIR: str = "forecasts"

DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_SILVER_DIR: str = "silver"
DATA_VALIDATION_REPORT_FILE_NAME: str = "validation_report.json"

DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_GOLD_DIR: str = "gold"

FEATURE_ENGINEERING_DIR_NAME: str = "feature_engineering"
FEATURE_ENGINEERING_FEATURES_DIR: str = "features"

DATASET_CREATION_DIR_NAME: str = "dataset_creation"
DATASET_MANIFEST_FILE_NAME: str = "dataset_manifest.json"

BASELINE_TRAINER_DIR_NAME: str = "baseline_trainer"
HYPERPARAMETER_TUNER_DIR_NAME: str = "hyperparameter_tuner"
MODEL_TRAINER_DIR_NAME: str = "model_trainer"
DEEP_TRAINER_DIR_NAME: str = "deep_trainer"

MODEL_EVALUATION_DIR_NAME: str = "model_evaluation"
MODEL_EVALUATION_LEADERBOARD_FILE: str = "leaderboard.json"
MODEL_EVALUATION_REPORT_FILE: str = "evaluation_report.json"
MODEL_EVALUATION_ERROR_ANALYSIS_FILE: str = "error_analysis.json"

MODEL_PUSHER_DIR_NAME: str = "model_pusher"
MODEL_PUSHER_GATE_FILE: str = "quality_gate.json"

MONITORING_DIR_NAME: str = "monitoring"
DRIFT_REPORT_FILE_NAME: str = "drift_report.json"
