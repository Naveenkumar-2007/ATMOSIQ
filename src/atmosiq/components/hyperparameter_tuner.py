import os
import sys

import optuna
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from atmosiq.components.model_trainer import feature_columns_for
from atmosiq.entity.artifact_entity import DatasetCreationArtifact, HyperparameterTunerArtifact
from atmosiq.entity.config_entity import HyperparameterTunerConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_parquet, write_json_file
from atmosiq.utils.ml_utils.metric import metrics as metric
from atmosiq.utils.ml_utils.model.factory import ModelFactory

logger = logging.getLogger("atmosiq.components.hyperparameter_tuner")

optuna.logging.set_verbosity(optuna.logging.WARNING)


class HyperparameterTuner:
    def __init__(self, dataset_artifact, config):
        try:
            self.dataset_artifact = dataset_artifact
            self.config = config
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _search_space(self, trial):
        return {
            "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "n_estimators": trial.suggest_int("n_estimators", 100, 800, step=50),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "min_child_weight": trial.suggest_float("min_child_weight", 1e-2, 10, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10, log=True),
            "n_jobs": 2,
            "verbosity": 0,
        }

    def initiate_tuning(self):
        try:
            train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
            features = feature_columns_for(train)
            best_params_all = {}
            trial_rows = []
            for horizon in (24, 48):
                target_col = f"target_temperature_{horizon}h"
                df = train.dropna(subset=[target_col] + [f for f in features if f in train.columns]).reset_index(drop=True)
                if df.empty:
                    continue
                X, y = df[features].to_numpy(), df[target_col].to_numpy()

                def objective(trial):
                    params = self._search_space(trial)
                    scores = []
                    tscv = TimeSeriesSplit(n_splits=self.config.cv_splits)
                    for tr_idx, va_idx in tscv.split(X):
                        model = ModelFactory.create("xgboost", "temperature", params)
                        model.fit(X[tr_idx], y[tr_idx])
                        scores.append(metric.mae(y[va_idx], model.predict(X[va_idx])))
                    return sum(scores) / len(scores)

                study = optuna.create_study(direction="minimize", pruner=optuna.pruners.MedianPruner())
                study.optimize(objective, n_trials=self.config.n_trials)
                best_params_all[f"xgboost@temperature@{horizon}"] = study.best_params
                for t in study.trials:
                    if t.value is not None:
                        trial_rows.append({"horizon": horizon, "trial": t.number, "params": str(t.params), "mae": t.value, "duration": str(t.duration)})
            write_json_file(os.path.join(self.config.tuner_dir, "best_params.json"), best_params_all)
            trials_path = os.path.join(self.config.tuner_dir, "trials.parquet")
            pd.DataFrame(trial_rows).to_parquet(trials_path, index=False)
            logger.info("tuning complete", extra={"ctx_trials": len(trial_rows)})
            return HyperparameterTunerArtifact(
                tuner_dir=self.config.tuner_dir,
                best_params_file_path=os.path.join(self.config.tuner_dir, "best_params.json"),
                trials_file_path=trials_path,
                best_params=best_params_all,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
