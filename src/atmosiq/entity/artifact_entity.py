from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    raw_dir: str
    bronze_dir: str
    forecast_dir: str
    ingestion_run_id: str
    observation_count: int
    forecast_count: int


@dataclass
class DataValidationArtifact:
    validation_status: bool
    silver_dir: str
    report_file_path: str
    validation_run_id: str
    rejected_rows: int


@dataclass
class DataTransformationArtifact:
    gold_dir: str
    preprocessor_file_path: str
    feature_metadata_file_path: str
    config_hash: str
    train_split_end: str


@dataclass
class FeatureEngineeringArtifact:
    features_dir: str
    feature_version_id: str
    feature_columns: list
    leakage_check_passed: bool


@dataclass
class DatasetCreationArtifact:
    dataset_dir: str
    manifest_file_path: str
    dataset_version_id: str
    train_rows: int
    validation_rows: int
    test_rows: int


@dataclass
class BaselineTrainerArtifact:
    baseline_dir: str
    baseline_predictions_file_path: str
    baseline_metrics: dict


@dataclass
class HyperparameterTunerArtifact:
    tuner_dir: str
    best_params_file_path: str
    trials_file_path: str
    best_params: dict


@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    model_name: str
    task: str
    horizon_hours: int
    train_metrics: dict
    validation_metrics: dict
    training_run_id: str


@dataclass
class ModelEvaluationArtifact:
    leaderboard_file_path: str
    report_file_path: str
    error_analysis_file_path: str
    gate_file_path: str
    gate_passed: bool
    champion_candidate: str


@dataclass
class ModelPusherArtifact:
    pushed: bool
    model_version_id: str
    stage: str
    message: str
