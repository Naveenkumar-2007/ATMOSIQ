import os
import sys

import numpy as np
import pandas as pd

from atmosiq.components.model_trainer import feature_columns_for
from atmosiq.components.task_registry import kind_of, is_classification
from atmosiq.entity.artifact_entity import BaselineTrainerArtifact, DatasetCreationArtifact, ModelEvaluationArtifact, ModelTrainerArtifact
from atmosiq.entity.config_entity import ModelEvaluationConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import load_object, read_parquet, write_json_file
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.model_evaluation")

WEATHER_CODE_REGIMES = {
    "clear": lambda r: r.get("weather_code", 0) is not None and r["weather_code"] <= 1,
    "cloudy": lambda r: r.get("weather_code", 0) is not None and 2 <= r["weather_code"] <= 3,
    "rainy": lambda r: r.get("weather_code", 0) is not None and 51 <= r["weather_code"] <= 67,
    "heavy_rain": lambda r: (r.get("weather_code", 0) is not None and 63 <= r["weather_code"] <= 67) or (r.get("precipitation", 0) or 0) >= 7.5,
    "storm": lambda r: r.get("weather_code", 0) is not None and 95 <= r["weather_code"] <= 99,
    "high_wind": lambda r: (r.get("wind_speed_10m", 0) or 0) >= 30,
    "extreme_heat": lambda r: (r.get("temperature_2m", 0) or 0) >= 40,
    "cold": lambda r: (r.get("temperature_2m", 0) or 0) <= 0,
}


def derive_regime(row):
    d = row.to_dict()
    for regime, rule in WEATHER_CODE_REGIMES.items():
        try:
            if rule(d):
                return regime
        except (TypeError, ValueError):
            continue
    return "moderate"


class ModelEvaluation:
    def __init__(self, dataset_artifact, trainer_artifacts, baseline_artifact, config):
        try:
            self.dataset_artifact = dataset_artifact
            self.trainer_artifacts = trainer_artifacts
            self.baseline_artifact = baseline_artifact
            self.config = config
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _evaluate_all(self, test):
        features = feature_columns_for(test)
        board = []
        baseline_df = read_parquet(self.baseline_artifact.baseline_predictions_file_path)
        for artifact in self.trainer_artifacts:
            if artifact.trained_model_file_path.endswith(".pt"):
                continue
            target_col = f"target_{artifact.task}_{artifact.horizon_hours}h"
            avail = [f for f in features if f in test.columns]
            usable = test.dropna(subset=[target_col]).copy()
            if usable.empty:
                continue
            for f in avail:
                usable[f] = usable[f].fillna(0.0)
            X = usable[avail].to_numpy()
            y = usable[target_col].to_numpy()
            blob = load_object(artifact.trained_model_file_path)
            estimator = blob["estimator"] if isinstance(blob, dict) else blob
            pred = estimator.predict(X)
            base = baseline_df[(baseline_df["model"] == "persistence") & (baseline_df["horizon"] == artifact.horizon_hours)]
            if is_classification(artifact.task):
                if kind_of(artifact.task) == "binary":
                    proba = estimator.predict_proba(X)[:, 1] if hasattr(estimator, "predict_proba") else pred
                    opt_th = artifact.validation_metrics.get("optimal_threshold", 0.5) if hasattr(artifact, "validation_metrics") and artifact.validation_metrics else 0.5
                    calibrated_pred = (proba >= opt_th).astype(int)
                    row = {
                        "model": artifact.model_name, "task": artifact.task, "horizon": artifact.horizon_hours,
                        "accuracy": metric.accuracy(y, calibrated_pred), "pr_auc": metric.pr_auc(y, proba),
                        "brier": metric.brier_score(y, proba), "f1": metric.f1(y, calibrated_pred),
                        "optimal_threshold": opt_th,
                    }
                else:
                    row = {
                        "model": artifact.model_name, "task": artifact.task, "horizon": artifact.horizon_hours,
                        "accuracy": metric.accuracy(y, pred), "macro_f1": metric.macro_f1(y, pred),
                    }
            else:
                baseline_pred = np.full(len(y), base["prediction"].mean()) if not base.empty else y
                row = {
                    "model": artifact.model_name, "task": artifact.task, "horizon": artifact.horizon_hours,
                    "mae": metric.mae(y, pred), "rmse": metric.rmse(y, pred),
                    "mase": metric.mase(y, pred), "skill_vs_persistence": metric.skill_score(y, pred, baseline_pred),
                }
            board.append(row)
        return board

    def _error_analysis(self, test):
        analysis = {"by_hour": {}, "by_month": {}, "by_horizon": {}, "by_regime": {}}
        t = pd.to_datetime(test["time"], utc=True)
        for horizon in self.config.app.horizons:
            col = f"target_temperature_{horizon}h"
            usable = test.dropna(subset=[col])
            if usable.empty:
                continue
            err = (usable["temperature_2m"] - usable[col]).abs()
            analysis["by_horizon"][str(horizon)] = float(err.mean())
        regime = test.apply(derive_regime, axis=1)
        for name, group in test.groupby(regime):
            analysis["by_regime"][str(name)] = int(len(group))
        analysis["by_hour"] = {str(h): int(c) for h, c in t.dt.hour.value_counts().sort_index().items()}
        analysis["by_month"] = {str(m): int(c) for m, c in t.dt.month.value_counts().sort_index().items()}
        return analysis

    def _quality_gate(self, board):
        policy = self.config.app.raw["quality_gate"]
        decisions = []
        for row in board:
            checks = {}
            if row["task"] == "temperature":
                checks["beats_persistence"] = bool(row["skill_vs_persistence"] > 0) if policy["must_beat_persistence"] else True
                checks["mase_ok"] = bool(row["mase"] < policy["max_mase"])
                checks["skill_ok"] = bool(row["skill_vs_persistence"] >= policy["min_skill_vs_persistence"])
            if row["task"] == "rain_occurrence":
                checks["pr_auc_ok"] = bool(row.get("pr_auc", 0) >= policy["min_rain_pr_auc"])
            if row["task"] == "weather_condition":
                checks["accuracy_ok"] = bool(row.get("accuracy", 0) >= policy["min_condition_accuracy"])
            row_passed = all(checks.values()) if checks else True
            decisions.append({"model": row["model"], "task": row["task"], "horizon": row["horizon"], "checks": checks, "passed": row_passed})
        passed_any = any(d["passed"] for d in decisions)
        return {"policy": policy, "decisions": decisions, "passed": passed_any}

    def initiate_model_evaluation(self):
        try:
            test = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "test.parquet"))
            board = self._evaluate_all(test)
            board.sort(key=lambda r: (r["task"], r["horizon"], r.get("mae", 0) or -r.get("accuracy", 0)))
            write_json_file(self.config.leaderboard_file_path, board)
            write_json_file(self.config.error_analysis_file_path, self._error_analysis(test))
            gate = self._quality_gate(board)
            write_json_file(self.config.gate_file_path, gate)
            candidate = ""
            for decision in gate["decisions"]:
                if decision["passed"]:
                    candidate = f"{decision['model']}@{decision['task']}@{decision['horizon']}"
                    break
            report = {"leaderboard_rows": len(board), "gate_passed": gate["passed"], "candidate": candidate}
            write_json_file(self.config.report_file_path, report)
            logger.info("evaluation complete", extra={"ctx_gate": gate["passed"]})
            return ModelEvaluationArtifact(
                leaderboard_file_path=self.config.leaderboard_file_path,
                report_file_path=self.config.report_file_path,
                error_analysis_file_path=self.config.error_analysis_file_path,
                gate_file_path=self.config.gate_file_path,
                gate_passed=gate["passed"],
                champion_candidate=candidate,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
