import sys
import uuid

from atmosiq.db.models import Deployment, ModelVersion
from atmosiq.db.repositories import ModelRegistryRepository
from atmosiq.entity.artifact_entity import (
    ModelPusherArtifact,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_json_file

logger = logging.getLogger("atmosiq.components.model_pusher")


class ModelPusher:
    def __init__(self, evaluation_artifact, trainer_artifacts, config, session, approved_by=None):
        try:
            self.evaluation_artifact = evaluation_artifact
            self.trainer_artifacts = trainer_artifacts
            self.config = config
            self.repo = ModelRegistryRepository(session)
            self.session = session
            self.approved_by = approved_by
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _mlflow_log(self, artifact):
        try:
            import mlflow
            mlflow.set_tracking_uri(self.config.mlflow_tracking_uri)
            mlflow.set_experiment("atmosiq")
            with mlflow.start_run(run_name=artifact.model_name):
                mlflow.log_params({"task": artifact.task, "horizon": artifact.horizon_hours})
                mlflow.log_metrics({k: v for k, v in artifact.validation_metrics.items() if isinstance(v, int | float)})
                mlflow.log_artifact(artifact.trained_model_file_path)
        except Exception as e:
            logger.warning(f"mlflow logging skipped: {e}")

    def initiate_model_pusher(self):
        try:
            if not self.trainer_artifacts:
                return ModelPusherArtifact(False, "", "Candidate", "no models trained")

            require_approval = self.config.app.raw["quality_gate"].get("require_manual_approval", False)
            gate = read_json_file(self.evaluation_artifact.gate_file_path) if getattr(self.evaluation_artifact, "gate_file_path", None) else {"decisions": []}
            promoted_count = 0
            primary_version_id = ""

            for chosen in self.trainer_artifacts:
                match = f"{chosen.model_name}@{chosen.task}@{chosen.horizon_hours}"
                decision = next((d for d in gate.get("decisions", []) if f"{d['model']}@{d['task']}@{d['horizon']}" == match), None)
                if decision is None or decision.get("passed", False):
                    self._mlflow_log(chosen)
                    version_id = f"mv_{uuid.uuid4().hex[:12]}"
                    if not primary_version_id:
                        primary_version_id = version_id
                    stage = "Champion" if not require_approval or self.approved_by else "Candidate"

                    if stage == "Champion":
                        prev = self.repo.champion(chosen.task, chosen.horizon_hours)
                        if prev is not None:
                            self.repo.set_stage(prev.id, "Retired")

                    self.repo.add_version(ModelVersion(
                        id=version_id, model_name=chosen.model_name, task=chosen.task, horizon_hours=chosen.horizon_hours,
                        stage=stage, training_run_id=chosen.training_run_id, artifact_path=chosen.trained_model_file_path, metrics=chosen.validation_metrics,
                    ))
                    if stage == "Champion":
                        self.repo.add_deployment(Deployment(
                            model_version_id=version_id, task=chosen.task, horizon_hours=chosen.horizon_hours,
                            action="promote", actor=self.approved_by or "system"
                        ))
                        promoted_count += 1

            if promoted_count > 0:
                logger.info(f"Promoted {promoted_count} models to Champion")
                return ModelPusherArtifact(True, primary_version_id, "Champion", f"{promoted_count} models promoted to Champion")
            else:
                return ModelPusherArtifact(False, primary_version_id, "Candidate", "candidates registered; awaiting manual approval")
        except Exception as e:
            raise AtmosIQException(e, sys)

    def promote(self, version_id):
        version = self.session.get(ModelVersion, version_id)
        if version is None:
            raise AtmosIQException(f"unknown model version {version_id}")
        champion = self.repo.champion(version.task, version.horizon_hours)
        if champion is not None:
            self.repo.set_stage(champion.id, "Retired")
        self.repo.set_stage(version_id, "Champion")
        self.repo.add_deployment(Deployment(model_version_id=version_id, task=version.task, horizon_hours=version.horizon_hours, action="promote", actor=self.approved_by or "system"))
        logger.info("model promoted", extra={"ctx_model_version": version_id})
        return ModelPusherArtifact(True, version_id, "Champion", "challenger passed gate and replaced champion; previous champion retired")

    def rollback(self, task, horizon_hours):
        versions = self.session.query(ModelVersion).filter_by(task=task, horizon_hours=horizon_hours, stage="Retired").order_by(ModelVersion.created_at.desc()).all()
        if not versions:
            raise AtmosIQException("no retired version available for rollback")
        current = self.repo.champion(task, horizon_hours)
        if current is not None:
            self.repo.set_stage(current.id, "Retired")
        self.repo.set_stage(versions[0].id, "Champion")
        self.repo.add_deployment(Deployment(model_version_id=versions[0].id, task=task, horizon_hours=horizon_hours, action="rollback"))
        return ModelPusherArtifact(True, versions[0].id, "Champion", "rollback complete")
