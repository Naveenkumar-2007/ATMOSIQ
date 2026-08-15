import sys

import click

from atmosiq.logging.logger import logging

logger = logging.getLogger("atmosiq.cli")


def _run(fn):
    try:
        return fn()
    except Exception as e:
        logger.error(f"command failed: {e}")
        sys.exit(1)


@click.group()
def cli():
    """AtmosIQ weather ML platform CLI."""


@cli.command()
def ingest():
    from atmosiq.components.data_ingestion import DataIngestion
    from atmosiq.db.session import get_session
    from atmosiq.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig
    from atmosiq.providers import get_provider

    def run():
        session = get_session()
        cfg = DataIngestionConfig(TrainingPipelineConfig())
        provider = get_provider(cfg.app.raw["provider"]["name"], cfg.app.raw["provider"])
        artifact = DataIngestion(cfg, provider, session).initiate_data_ingestion()
        click.echo(f"Ingested {artifact.observation_count} observations, {artifact.forecast_count} forecasts")
    _run(run)


@cli.command()
def validate():
    from atmosiq.components.data_ingestion import DataIngestion
    from atmosiq.components.data_validation import DataValidation
    from atmosiq.db.session import get_session
    from atmosiq.entity.config_entity import (
        DataIngestionConfig,
        DataValidationConfig,
        TrainingPipelineConfig,
    )
    from atmosiq.providers import get_provider

    def run():
        session = get_session()
        pipe_cfg = TrainingPipelineConfig()
        ingest_cfg = DataIngestionConfig(pipe_cfg)
        provider = get_provider(ingest_cfg.app.raw["provider"]["name"], ingest_cfg.app.raw["provider"])
        ingestion_artifact = DataIngestion(ingest_cfg, provider, session).initiate_data_ingestion()
        validation_cfg = DataValidationConfig(pipe_cfg)
        validation_artifact = DataValidation(ingestion_artifact, validation_cfg, session).initiate_data_validation()
        click.echo(
            f"Validation complete. Status: {validation_artifact.validation_status}, "
            f"Silver dir: {validation_artifact.silver_dir}, "
            f"Rejected rows: {validation_artifact.rejected_rows}"
        )
    _run(run)


@cli.command()
def train():
    from atmosiq.db.session import get_session
    from atmosiq.pipeline.training_pipeline import TrainingPipeline

    def run():
        session = get_session()
        pipeline = TrainingPipeline(session=session, deep=False, tune=False)
        artifacts = pipeline.run()
        click.echo(f"Pipeline complete. Gate passed: {artifacts['evaluation'].gate_passed}")
        click.echo(f"Pusher stage: {artifacts['pusher'].stage}")
    _run(run)


@cli.command()
@click.option("--approved-by", default=None)
def promote(approved_by):
    def run():
        click.echo(f"Promotion requires a trained challenger; run 'train' first. Approver: {approved_by or 'none'}")
    _run(run)


@cli.command()
@click.option("--task", required=True)
@click.option("--horizon", type=int, required=True)
@click.option("--location", default="kavali", help="Location ID (e.g. kavali, hyderabad, bengaluru)")
def predict(task, horizon, location):
    from atmosiq.components.prediction_service import PredictionService
    from atmosiq.db.session import get_session

    def run():
        session = get_session()
        service = PredictionService(session)
        result = service.predict(task, horizon, {}, location_id=location)
        click.echo(f"Prediction: {result}")
    _run(run)



@cli.command()
def monitor():
    from atmosiq.db.session import get_session
    from atmosiq.pipeline.monitoring_pipeline import MonitoringPipeline

    def run():
        session = get_session()
        result = MonitoringPipeline(session).run_cycle()
        click.echo(f"Monitoring: {result}")
    _run(run)


@cli.command()
@click.option("--reason", default="manual")
def retrain(reason):
    from atmosiq.components.retraining_service import RetrainingService
    from atmosiq.db.session import get_session

    def run():
        session = get_session()
        service = RetrainingService(session)
        result = service.run_retraining(reason)
        click.echo(f"Retraining complete. Stage: {result['pusher'].stage}")
    _run(run)


@cli.command()
def db_migrate():
    import subprocess

    def run():
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        if result.returncode != 0:
            click.echo(result.stderr)
            sys.exit(1)
        click.echo("Migrations applied.")
    _run(run)


if __name__ == "__main__":
    cli()
