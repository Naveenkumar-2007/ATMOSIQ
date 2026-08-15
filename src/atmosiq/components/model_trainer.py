import os
import platform
import sys
import time
import uuid

import numpy as np
import pandas as pd

from atmosiq.components.task_registry import TASKS, is_classification
from atmosiq.db.models import TrainingRun
from atmosiq.entity.artifact_entity import (
    ModelTrainerArtifact,
)
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_json_file, read_parquet
from atmosiq.utils.ml_utils.metric import metrics as metric
from atmosiq.utils.ml_utils.model.factory import ModelFactory

logger = logging.getLogger("atmosiq.components.model_trainer")

FEATURE_TOKENS = ("s_", "_lag_", "_mean_", "_std_", "_sin", "_cos")
FEATURE_EXACT = {
    "hour", "day", "day_of_week", "day_of_year", "week", "month", "season",
    "pressure_change_3h", "pressure_change_6h", "pressure_tendency",
    "dew_point_depression", "apparent_temperature_difference",
    "provider_forecast_lead_time", "recent_provider_bias", "recent_provider_mae", "recent_provider_error",
    "latitude", "longitude", "elevation",
}


def feature_columns_for(df):
    cols = []
    for c in df.columns:
        if c in ("time", "location_id") or c.startswith("target_") or c.startswith("forecast_issue_time"):
            continue
        if c in FEATURE_EXACT or c.startswith(FEATURE_TOKENS) or c.startswith("provider_"):
            if not df[c].isna().all():
                cols.append(c)
    return sorted(set(cols))


class ModelTrainer:
    def __init__(self, dataset_artifact, feature_artifact, config, session=None, tuner_artifact=None):
        try:
            self.dataset_artifact = dataset_artifact
            self.feature_artifact = feature_artifact
            self.config = config
            self.session = session
            self.tuner_artifact = tuner_artifact
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _environment(self):
        return {"python": platform.python_version(), "platform": platform.platform(), "packages": {"pandas": pd.__version__}}

    def initiate_model_training(self):
        try:
            train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
            validation = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "validation.parquet"))
            features = feature_columns_for(train)
            artifacts = []
            best_params = read_json_file(self.tuner_artifact.best_params_file_path) if self.tuner_artifact is not None else {}
            for task, (source, kind, horizons) in TASKS.items():
                for horizon in horizons:
                    target_col = f"target_{task}_{horizon}h"
                    avail = [f for f in features if f in train.columns and f in validation.columns]
                    tr = train.dropna(subset=[target_col]).copy()
                    va = validation.dropna(subset=[target_col]).copy()
                    if tr.empty or va.empty:
                        continue
                    for f in avail:
                        tr[f] = tr[f].fillna(0.0)
                        va[f] = va[f].fillna(0.0)
                    X_tr, y_tr = tr[avail].to_numpy(), tr[target_col].to_numpy()
                    X_va, y_va = va[avail].to_numpy(), va[target_col].to_numpy()

                    pos_count = int((y_tr == 1).sum()) if kind == "binary" else 0
                    neg_count = int((y_tr == 0).sum()) if kind == "binary" else 0
                    pos_weight = float(neg_count / max(pos_count, 1)) if pos_count > 0 else 1.0

                    model_names = self.config.rain_classifiers if is_classification(task) else self.config.classical_models
                    for name in model_names:
                        started = time.monotonic()
                        params = best_params.get(f"{name}@{task}@{horizon}", {}).copy()
                        if is_classification(task) and kind == "binary":
                            if "scale_pos_weight" not in params:
                                params["scale_pos_weight"] = pos_weight

                        model = ModelFactory.create(name, "rain_occurrence" if is_classification(task) else task, params)
                        model.fit(X_tr, y_tr)
                        pred = model.predict(X_va)
                        if is_classification(task):
                            if kind == "binary":
                                proba = model.predict_proba(X_va)
                                p1 = proba[:, 1] if proba.ndim == 2 else proba
                                best_thresh = 0.5
                                best_f1 = -1.0
                                for th in np.linspace(0.05, 0.95, 46):
                                    f = metric.f1(y_va, (p1 >= th).astype(int))
                                    if f > best_f1:
                                        best_f1 = f
                                        best_thresh = float(th)
                                val_metrics = {
                                    "accuracy": metric.accuracy(y_va, pred), "precision": metric.precision(y_va, pred),
                                    "recall": metric.recall(y_va, pred), "f1": metric.f1(y_va, pred),
                                    "tuned_f1": round(best_f1, 4), "optimal_threshold": round(best_thresh, 3),
                                    "roc_auc": metric.roc_auc(y_va, proba), "pr_auc": metric.pr_auc(y_va, proba),
                                    "brier": metric.brier_score(y_va, proba), "log_loss": metric.log_loss(y_va, proba),
                                }
                            else:
                                val_metrics = {"accuracy": metric.accuracy(y_va, pred), "macro_f1": metric.macro_f1(y_va, pred)}
                        else:
                            val_metrics = {"mae": metric.mae(y_va, pred), "rmse": metric.rmse(y_va, pred), "r2": metric.r2(y_va, pred)}
                        run_id = f"tr_{uuid.uuid4().hex[:12]}"
                        model_path = os.path.join(self.config.model_trainer_dir, task, f"{horizon}h", f"{name}.pkl")
                        model.save(model_path)
                        if self.session is not None:
                            self.session.add(TrainingRun(
                                id=run_id, model_name=name, task=task, horizon_hours=horizon,
                                dataset_version_id=self.dataset_artifact.dataset_version_id,
                                feature_version_id=self.feature_artifact.feature_version_id,
                                hyperparameters=params, metrics=val_metrics, seed=42,
                                duration_seconds=round(time.monotonic() - started, 2), environment=self._environment(),
                            ))
                            self.session.commit()
                        artifacts.append(ModelTrainerArtifact(
                            trained_model_file_path=model_path, model_name=name, task=task, horizon_hours=horizon,
                            train_metrics={"rows": int(len(tr))}, validation_metrics=val_metrics, training_run_id=run_id,
                        ))
            logger.info("model training complete", extra={"ctx_models": len(artifacts)})
            return artifacts
        except Exception as e:
            raise AtmosIQException(e, sys)
