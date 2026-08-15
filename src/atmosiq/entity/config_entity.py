import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from atmosiq.constant import training_pipeline as tp
from atmosiq.utils.main_utils.utils import read_yaml_file


@dataclass
class TrainingPipelineConfig:
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%m_%d_%Y_%H_%M_%S"))
    pipeline_name: str = tp.PIPELINE_NAME
    artifact_name: str = tp.ARTIFACT_DIR
    artifact_dir: str = ""

    def __post_init__(self):
        self.artifact_dir = os.path.join(self.artifact_name, self.timestamp)


@dataclass
class AppConfig:
    raw: dict = field(default_factory=lambda: read_yaml_file(tp.CONFIG_FILE_PATH))

    @property
    def locations(self):
        return self.raw["locations"]

    @property
    def horizons(self):
        return self.raw.get("horizons", tp.HORIZONS)

    @property
    def splits(self):
        return self.raw["splits"]


@dataclass
class DataIngestionConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    data_ingestion_dir: str = ""
    raw_dir: str = ""
    bronze_dir: str = ""
    forecast_dir: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATA_INGESTION_DIR_NAME)
        self.data_ingestion_dir = base
        self.raw_dir = os.path.join(base, tp.DATA_INGESTION_RAW_DIR)
        self.bronze_dir = os.path.join(base, tp.DATA_INGESTION_BRONZE_DIR)
        self.forecast_dir = os.path.join(base, tp.DATA_INGESTION_FORECAST_DIR)


@dataclass
class DataValidationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    data_validation_dir: str = ""
    silver_dir: str = ""
    report_file_path: str = ""
    schema_file_path: str = tp.SCHEMA_FILE_PATH

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATA_VALIDATION_DIR_NAME)
        self.data_validation_dir = base
        self.silver_dir = os.path.join(base, tp.DATA_VALIDATION_SILVER_DIR)
        self.report_file_path = os.path.join(base, tp.DATA_VALIDATION_REPORT_FILE_NAME)


@dataclass
class DataTransformationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    data_transformation_dir: str = ""
    gold_dir: str = ""
    preprocessor_file_path: str = ""
    feature_metadata_file_path: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATA_TRANSFORMATION_DIR_NAME)
        self.data_transformation_dir = base
        self.gold_dir = os.path.join(base, tp.DATA_TRANSFORMATION_GOLD_DIR)
        self.preprocessor_file_path = os.path.join(base, tp.PREPROCESSING_OBJECT_FILE_NAME)
        self.feature_metadata_file_path = os.path.join(base, tp.FEATURE_METADATA_FILE_NAME)


@dataclass
class FeatureEngineeringConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    feature_engineering_dir: str = ""
    features_dir: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.FEATURE_ENGINEERING_DIR_NAME)
        self.feature_engineering_dir = base
        self.features_dir = os.path.join(base, tp.FEATURE_ENGINEERING_FEATURES_DIR)


@dataclass
class DatasetCreationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    dataset_dir: str = ""
    manifest_file_path: str = ""

    def __post_init__(self):
        self.dataset_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.DATASET_CREATION_DIR_NAME)
        self.manifest_file_path = os.path.join(self.dataset_dir, tp.DATASET_MANIFEST_FILE_NAME)


@dataclass
class BaselineTrainerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    baseline_dir: str = ""

    def __post_init__(self):
        self.baseline_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.BASELINE_TRAINER_DIR_NAME)


@dataclass
class HyperparameterTunerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    tuner_dir: str = ""
    n_trials: int = 40
    cv_splits: int = 3

    def __post_init__(self):
        self.tuner_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.HYPERPARAMETER_TUNER_DIR_NAME)
        self.n_trials = int(self.app.raw.get("tuning", {}).get("n_trials", self.n_trials))
        self.cv_splits = int(self.app.raw.get("tuning", {}).get("cv_splits", self.cv_splits))


@dataclass
class ModelTrainerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    classical_models: list = field(default_factory=lambda: ["ridge", "random_forest", "xgboost", "lightgbm", "catboost", "hist_gb"])
    rain_classifiers: list = field(default_factory=lambda: ["logistic_regression", "random_forest_clf", "xgboost_clf", "lightgbm_clf", "catboost_clf", "hist_gb_clf"])

    def __post_init__(self):
        self.model_trainer_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.MODEL_TRAINER_DIR_NAME)


@dataclass
class DeepTrainerConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    deep_dir: str = ""
    sequence_length: int = 48
    epochs: int = 30
    batch_size: int = 128
    patience: int = 5

    def __post_init__(self):
        self.deep_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.DEEP_TRAINER_DIR_NAME)
        deep = self.app.raw.get("deep", {})
        self.sequence_length = int(deep.get("sequence_length", self.sequence_length))
        self.epochs = int(deep.get("epochs", self.epochs))
        self.batch_size = int(deep.get("batch_size", self.batch_size))
        self.patience = int(deep.get("patience", self.patience))


@dataclass
class ModelEvaluationConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    evaluation_dir: str = ""
    leaderboard_file_path: str = ""
    report_file_path: str = ""
    error_analysis_file_path: str = ""
    gate_file_path: str = ""

    def __post_init__(self):
        base = os.path.join(self.training_pipeline_config.artifact_dir, tp.MODEL_EVALUATION_DIR_NAME)
        self.evaluation_dir = base
        self.leaderboard_file_path = os.path.join(base, tp.MODEL_EVALUATION_LEADERBOARD_FILE)
        self.report_file_path = os.path.join(base, tp.MODEL_EVALUATION_REPORT_FILE)
        self.error_analysis_file_path = os.path.join(base, tp.MODEL_EVALUATION_ERROR_ANALYSIS_FILE)
        self.gate_file_path = os.path.join(base, tp.MODEL_PUSHER_GATE_FILE)


@dataclass
class ModelPusherConfig:
    training_pipeline_config: TrainingPipelineConfig
    app: AppConfig = field(default_factory=AppConfig)
    pusher_dir: str = ""
    mlflow_tracking_uri: str = ""

    def __post_init__(self):
        import os as _os
        self.pusher_dir = os.path.join(self.training_pipeline_config.artifact_dir, tp.MODEL_PUSHER_DIR_NAME)
        self.mlflow_tracking_uri = _os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
