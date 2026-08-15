import sys

from atmosiq.components.baseline_trainer import BaselineTrainer
from atmosiq.components.data_ingestion import DataIngestion
from atmosiq.components.data_transformation import DataTransformation
from atmosiq.components.data_validation import DataValidation
from atmosiq.components.dataset_creation import DatasetCreation
from atmosiq.components.deep.trainer import DeepTrainer
from atmosiq.components.feature_engineering import FeatureEngineering
from atmosiq.components.hyperparameter_tuner import HyperparameterTuner
from atmosiq.components.model_evaluation import ModelEvaluation
from atmosiq.components.model_pusher import ModelPusher
from atmosiq.components.model_trainer import ModelTrainer
from atmosiq.components.quantile_trainer import QuantileTrainer
from atmosiq.entity.config_entity import (
    BaselineTrainerConfig,
    DataIngestionConfig,
    DatasetCreationConfig,
    DataTransformationConfig,
    DataValidationConfig,
    DeepTrainerConfig,
    FeatureEngineeringConfig,
    HyperparameterTunerConfig,
    ModelEvaluationConfig,
    ModelPusherConfig,
    ModelTrainerConfig,
    TrainingPipelineConfig,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.providers import get_provider

logger = logging.getLogger("atmosiq.pipeline.training_pipeline")


class TrainingPipeline:
    def __init__(self, session=None, approved_by=None, deep=True, tune=True):
        self.pipeline_config = TrainingPipelineConfig()
        self.session = session
        self.approved_by = approved_by
        self.deep = deep
        self.tune = tune

    def run(self):
        try:
            ingestion_config = DataIngestionConfig(self.pipeline_config)
            app_cfg = ingestion_config.app
            provider = get_provider(app_cfg.raw["provider"]["name"], app_cfg.raw["provider"])

            ingestion_artifact = DataIngestion(ingestion_config, provider, self.session).initiate_data_ingestion()
            validation_artifact = DataValidation(ingestion_artifact, DataValidationConfig(self.pipeline_config), self.session).initiate_data_validation()
            transformation_artifact = DataTransformation(validation_artifact, DataTransformationConfig(self.pipeline_config)).initiate_data_transformation()
            feature_artifact = FeatureEngineering(transformation_artifact, FeatureEngineeringConfig(self.pipeline_config), self.session).initiate_feature_engineering()
            dataset_artifact = DatasetCreation(feature_artifact, DatasetCreationConfig(self.pipeline_config), self.session).initiate_dataset_creation()
            baseline_artifact = BaselineTrainer(dataset_artifact, BaselineTrainerConfig(self.pipeline_config)).initiate_baseline_training()

            tuner_artifact = None
            if self.tune:
                tuner_artifact = HyperparameterTuner(dataset_artifact, HyperparameterTunerConfig(self.pipeline_config)).initiate_tuning()

            trainer_artifacts = ModelTrainer(dataset_artifact, feature_artifact, ModelTrainerConfig(self.pipeline_config), self.session, tuner_artifact).initiate_model_training()
            QuantileTrainer(dataset_artifact, ModelTrainerConfig(self.pipeline_config), self.session).initiate_quantile_training()

            all_artifacts = list(trainer_artifacts)
            if self.deep:
                all_artifacts += DeepTrainer(dataset_artifact, DeepTrainerConfig(self.pipeline_config)).initiate_deep_training()

            evaluation_artifact = ModelEvaluation(dataset_artifact, all_artifacts, baseline_artifact, ModelEvaluationConfig(self.pipeline_config)).initiate_model_evaluation()
            pusher_artifact = ModelPusher(evaluation_artifact, all_artifacts, ModelPusherConfig(self.pipeline_config), self.session, self.approved_by).initiate_model_pusher()

            return {
                "ingestion": ingestion_artifact,
                "validation": validation_artifact,
                "transformation": transformation_artifact,
                "features": feature_artifact,
                "dataset": dataset_artifact,
                "baselines": baseline_artifact,
                "evaluation": evaluation_artifact,
                "pusher": pusher_artifact,
            }
        except Exception as e:
            raise AtmosIQException(e, sys)
