import os

from atmosiq.components.data_validation import DataValidation
from atmosiq.entity.artifact_entity import DataIngestionArtifact
from atmosiq.entity.config_entity import DataValidationConfig, TrainingPipelineConfig
from atmosiq.utils.main_utils.utils import save_parquet


def _make(project_root, real_observation_df):
    bronze = os.path.join(project_root, "bronze")
    os.makedirs(bronze, exist_ok=True)
    save_parquet(real_observation_df, os.path.join(bronze, "test_hourly.parquet"))
    artifact = DataIngestionArtifact(
        raw_dir="", bronze_dir=bronze, forecast_dir="", ingestion_run_id="t",
        observation_count=len(real_observation_df), forecast_count=0,
    )
    return artifact, DataValidationConfig(TrainingPipelineConfig())


def test_valid_data_passes(project_root, real_observation_df):
    artifact, cfg = _make(project_root, real_observation_df)
    result = DataValidation(artifact, cfg).initiate_data_validation()
    assert result.validation_status is True
    assert result.rejected_rows == 0


def test_out_of_range_rejected(project_root, real_observation_df):
    bad = real_observation_df.copy()
    bad.loc[0, "temperature_2m"] = 200.0
    artifact, cfg = _make(project_root, bad)
    result = DataValidation(artifact, cfg).initiate_data_validation()
    assert result.rejected_rows >= 1
