import os
import sys

import numpy as np
import pandas as pd

from atmosiq.entity.artifact_entity import BaselineTrainerArtifact, DatasetCreationArtifact
from atmosiq.entity.config_entity import BaselineTrainerConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_parquet, save_parquet, write_json_file
from atmosiq.utils.ml_utils.metric import metrics as metric
from atmosiq.utils.ml_utils.model.factory import ModelFactory

logger = logging.getLogger("atmosiq.components.baseline_trainer")

BASELINES = ["persistence", "seasonal_naive_24h", "seasonal_naive_168h", "climatology"]


class BaselineTrainer:
    def __init__(self, dataset_artifact, config):
        try:
            self.dataset_artifact = dataset_artifact
            self.config = config
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _baseline_features(self, df):
        return np.column_stack([
            df["temperature_2m"].to_numpy(),
            df["temperature_lag_24"].to_numpy(),
            df["temperature_lag_48"].to_numpy(),
            df["hour"].to_numpy(),
            df["month"].to_numpy(),
        ])

    def initiate_baseline_training(self):
        try:
            train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
            validation = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "validation.parquet"))
            results = {}
            frames = []
            for horizon in self.config.app.horizons:
                target_col = f"target_temperature_{horizon}h"
                usable = train.dropna(subset=[target_col])
                val_usable = validation.dropna(subset=[target_col])
                if usable.empty or val_usable.empty:
                    continue
                y_tr = usable[target_col].to_numpy()
                y_val = val_usable[target_col].to_numpy()
                X_tr = self._baseline_features(usable)
                X_val = self._baseline_features(val_usable)
                for name in BASELINES:
                    model = ModelFactory.create_baseline(name, horizon)
                    if name == "climatology":
                        model.fit(X_tr, y_tr, hour=usable["hour"], month=usable["month"])
                        pred = model.predict(X_val, hour=val_usable["hour"], month=val_usable["month"])
                    else:
                        model.fit(X_tr, y_tr)
                        pred = model.predict(X_val)
                    results[f"{name}@{horizon}h"] = {"mae": metric.mae(y_val, pred), "rmse": metric.rmse(y_val, pred)}
                    frames.append(pd.DataFrame({"time": val_usable["time"], "model": name, "horizon": horizon, "prediction": pred, "actual": y_val}))
            predictions_path = os.path.join(self.config.baseline_dir, "baseline_predictions.parquet")
            save_parquet(pd.concat(frames, ignore_index=True), predictions_path)
            write_json_file(os.path.join(self.config.baseline_dir, "baseline_metrics.json"), results)
            logger.info("baselines trained", extra={"ctx_baselines": len(results)})
            return BaselineTrainerArtifact(
                baseline_dir=self.config.baseline_dir,
                baseline_predictions_file_path=predictions_path,
                baseline_metrics=results,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
