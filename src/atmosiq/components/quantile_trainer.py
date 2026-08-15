import os
import uuid

from atmosiq.components.model_trainer import feature_columns_for
from atmosiq.components.quantile_models import QuantileEnsemble
from atmosiq.db.models import ModelVersion, TrainingRun
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_parquet, save_object
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.quantile_trainer")

QUANTILE_TASKS = [("temperature", 24), ("temperature", 6), ("precipitation_amount", 24)]


class QuantileTrainer:
    def __init__(self, dataset_artifact, config, session=None):
        self.dataset_artifact = dataset_artifact
        self.config = config
        self.session = session

    def initiate_quantile_training(self):
        train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
        validation = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "validation.parquet"))
        features = feature_columns_for(train)
        paths = []
        for task, horizon in QUANTILE_TASKS:
            target_col = f"target_{task}_{horizon}h"
            tr = train.dropna(subset=[target_col] + [f for f in features if f in train.columns])
            va = validation.dropna(subset=[target_col] + [f for f in features if f in validation.columns])
            if tr.empty or va.empty:
                continue
            X_tr, y_tr = tr[features].to_numpy(), tr[target_col].to_numpy()
            X_va, y_va = va[features].to_numpy(), va[target_col].to_numpy()
            ensemble = QuantileEnsemble("lightgbm", (0.1, 0.5, 0.9)).fit(X_tr, y_tr)
            q = ensemble.predict_quantiles(X_va)
            val_metrics = {
                "pinball_10": metric.pinball_loss(y_va, q[:, 0], 0.1),
                "pinball_50": metric.pinball_loss(y_va, q[:, 1], 0.5),
                "pinball_90": metric.pinball_loss(y_va, q[:, 2], 0.9),
                "coverage_10_90": metric.coverage(y_va, q[:, 0], q[:, 2]),
                "interval_width": metric.interval_width(q[:, 0], q[:, 2]),
            }
            run_id = f"tr_{uuid.uuid4().hex[:12]}"
            path = os.path.join(self.config.model_trainer_dir, "quantile", f"{task}_{horizon}h.pkl")
            save_object(path, ensemble)
            if self.session is not None:
                self.session.add(TrainingRun(id=run_id, model_name="quantile_lightgbm", task=f"{task}_quantile", horizon_hours=horizon, dataset_version_id=self.dataset_artifact.dataset_version_id, metrics=val_metrics, seed=42))
                self.session.commit()
                self.session.add(ModelVersion(id=f"mv_{uuid.uuid4().hex[:12]}", model_name="quantile_lightgbm", task=f"{task}_quantile", horizon_hours=horizon, stage="Champion", training_run_id=run_id, artifact_path=path, metrics=val_metrics))
                self.session.commit()
            logger.info("quantile trained", extra={"ctx_task": task, "ctx_horizon": horizon, "ctx_coverage": round(val_metrics["coverage_10_90"], 3)})
            paths.append(path)
        return paths
