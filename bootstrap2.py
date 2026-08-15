# bootstrap2.py  ->  run: python bootstrap2.py   (inside AtmosIQ/)
import os

W = {}

W["src/atmosiq/components/__init__.py"] = r'''
"""Components package (NetworkSecurity component contract)."""
'''

W["src/atmosiq/components/data_ingestion.py"] = r'''
import os
import sys
import uuid

from atmosiq.common.timeutils import now_utc
from atmosiq.db.models import IngestionRun
from atmosiq.db.repositories import ForecastRepository, LocationRepository, ObservationRepository, RunRepository
from atmosiq.entity.artifact_entity import DataIngestionArtifact
from atmosiq.entity.config_entity import DataIngestionConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.data_ingestion")


class DataIngestion:
    def __init__(self, data_ingestion_config, provider, session=None):
        try:
            self.config = data_ingestion_config
            self.provider = provider
            self.session = session
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _ingest_location(self, location):
        historical = self.provider.fetch_historical(
            location,
            self.config.app.raw["historical"]["start_date"],
            self.config.app.raw["historical"]["end_date"],
        )
        write_json_file(os.path.join(self.config.raw_dir, f"{location['id']}_historical_raw.json"), historical.raw)
        save_parquet(historical.hourly, os.path.join(self.config.bronze_dir, f"{location['id']}_hourly.parquet"))
        if not historical.daily.empty:
            save_parquet(historical.daily, os.path.join(self.config.bronze_dir, f"{location['id']}_daily.parquet"))
        obs_count = 0
        fc_count = 0
        if self.session is not None:
            LocationRepository(self.session).upsert(self.config.app.locations)
            obs_count = ObservationRepository(self.session).upsert_observations(location["id"], self.provider.name, historical.hourly)
            forecast = self.provider.fetch_forecast(location)
            save_parquet(forecast.hourly, os.path.join(self.config.forecast_dir, f"{location['id']}_forecast.parquet"))
            write_json_file(os.path.join(self.config.forecast_dir, f"{location['id']}_forecast_raw.json"), forecast.raw)
            fc_count = ForecastRepository(self.session).store_forecast_run(location["id"], self.provider.name, forecast.issue_time, forecast.meta.request_id, forecast.hourly)
        return obs_count, fc_count

    def initiate_data_ingestion(self):
        try:
            run_id = f"ing_{uuid.uuid4().hex[:12]}"
            total_obs = 0
            total_fc = 0
            for location in self.config.app.locations:
                logger.info("ingesting location", extra={"ctx_location_id": location["id"]})
                obs, fc = self._ingest_location(location)
                total_obs += obs
                total_fc += fc
                if self.session is not None:
                    RunRepository(self.session).add_ingestion_run(IngestionRun(
                        id=f"{run_id}_{location['id']}", location_id=location["id"], provider=self.provider.name,
                        started_at=now_utc(), finished_at=now_utc(), status="success",
                        observation_count=obs, forecast_count=fc, meta={"run_id": run_id},
                    ))
            return DataIngestionArtifact(
                raw_dir=self.config.raw_dir, bronze_dir=self.config.bronze_dir, forecast_dir=self.config.forecast_dir,
                ingestion_run_id=run_id, observation_count=total_obs, forecast_count=total_fc,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/data_validation.py"] = r'''
import os
import sys
import uuid

import pandas as pd

from atmosiq.db.models import ValidationRun
from atmosiq.db.repositories import RunRepository
from atmosiq.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from atmosiq.entity.config_entity import DataValidationConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_parquet, read_yaml_file, save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.data_validation")


class DataValidation:
    def __init__(self, data_ingestion_artifact, data_validation_config, session=None):
        try:
            self.ingestion_artifact = data_ingestion_artifact
            self.config = data_validation_config
            self.session = session
            self.schema = read_yaml_file(self.config.schema_file_path)["canonical_hourly"]
            self.ranges = self.config.app.raw["validation"]["ranges"]
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _check_dataframe(self, df):
        issues = []
        missing_cols = [c for c in self.schema if c not in df.columns]
        if missing_cols:
            issues.append(f"missing columns: {missing_cols}")
        df = df.sort_values("time")
        dup_count = int(df["time"].duplicated().sum())
        if dup_count:
            issues.append(f"duplicate timestamps: {dup_count}")
            df = df.drop_duplicates(subset=["time"])
        diffs = pd.to_datetime(df["time"], utc=True).diff().dropna()
        max_gap = self.config.app.raw["validation"]["max_gap_hours"]
        big_gaps = int((diffs > pd.Timedelta(hours=max_gap)).sum())
        if big_gaps:
            issues.append(f"abnormal provider gaps: {big_gaps}")
        if (diffs < pd.Timedelta(0)).any():
            issues.append("impossible timestamp sequence")
        rejected = pd.Series(False, index=df.index)
        for column, (low, high) in self.ranges.items():
            if column in df.columns:
                out = (df[column] < low) | (df[column] > high)
                rejected |= out.fillna(False)
        common = [c for c in self.ranges if c in df.columns]
        nan_frac = float(df[common].isna().mean().mean()) if common else 0.0
        if nan_frac > self.config.app.raw["validation"]["max_missing_fraction"]:
            issues.append(f"missingness {nan_frac:.3f} above threshold")
        df = df[~rejected]
        return issues, df

    def initiate_data_validation(self):
        try:
            report = {}
            status = True
            total_rejected = 0
            for file_name in sorted(os.listdir(self.ingestion_artifact.bronze_dir)):
                if not file_name.endswith("_hourly.parquet"):
                    continue
                location_id = file_name.replace("_hourly.parquet", "")
                df = read_parquet(os.path.join(self.ingestion_artifact.bronze_dir, file_name))
                before = len(df)
                issues, clean = self._check_dataframe(df)
                total_rejected += before - len(clean)
                if issues:
                    status = False
                report[location_id] = {"issues": issues, "rows_in": before, "rows_out": len(clean)}
                save_parquet(clean, os.path.join(self.config.silver_dir, file_name))
            write_json_file(self.config.report_file_path, report)
            run_id = f"val_{uuid.uuid4().hex[:12]}"
            if self.session is not None:
                RunRepository(self.session).add_validation_run(ValidationRun(
                    id=run_id, ingestion_run_id=self.ingestion_artifact.ingestion_run_id,
                    status="pass" if status else "fail", rejected_rows=total_rejected, report=report,
                ))
            logger.info("validation complete", extra={"ctx_status": status, "ctx_rejected": total_rejected})
            return DataValidationArtifact(
                validation_status=status, silver_dir=self.config.silver_dir,
                report_file_path=self.config.report_file_path, validation_run_id=run_id, rejected_rows=total_rejected,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/data_transformation.py"] = r'''
import os
import sys

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from atmosiq.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from atmosiq.entity.config_entity import DataTransformationConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.leakage_guard import LeakageGuard
from atmosiq.utils.main_utils.utils import hash_config, read_parquet, save_object, save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.data_transformation")

SCALE_COLUMNS = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
    "pressure_msl", "surface_pressure", "cloud_cover", "wind_speed_10m", "wind_gusts_10m",
]


class DataTransformation:
    def __init__(self, data_validation_artifact, data_transformation_config):
        try:
            self.validation_artifact = data_validation_artifact
            self.config = data_transformation_config
            self.guard = LeakageGuard()
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _load_all(self):
        frames = []
        for file_name in sorted(os.listdir(self.validation_artifact.silver_dir)):
            if file_name.endswith("_hourly.parquet"):
                location_id = file_name.replace("_hourly.parquet", "")
                df = read_parquet(os.path.join(self.validation_artifact.silver_dir, file_name))
                df["location_id"] = location_id
                frames.append(df)
        return pd.concat(frames, ignore_index=True).sort_values(["location_id", "time"])

    def get_data_transformer_object(self, train_df):
        scaler = StandardScaler()
        scaler.fit(train_df[SCALE_COLUMNS])
        return Pipeline([("scaler", scaler)])

    def initiate_data_transformation(self):
        try:
            df = self._load_all()
            splits = self.config.app.splits
            times = pd.to_datetime(df["time"], utc=True).sort_values().unique()
            train_end = times[int(len(times) * splits["train"]) - 1]
            train_df = df[pd.to_datetime(df["time"], utc=True) <= train_end]
            preprocessor = self.get_data_transformer_object(train_df)
            self.guard.assert_preprocessor_fit_bounds(
                pd.to_datetime(train_df["time"], utc=True).max().to_pydatetime(), train_end.to_pydatetime()
            )
            for location_id, group in df.groupby("location_id"):
                scaled = preprocessor.transform(group[SCALE_COLUMNS])
                out = group.copy()
                for i, column in enumerate(SCALE_COLUMNS):
                    out[f"s_{column}"] = scaled[:, i]
                save_parquet(out, os.path.join(self.config.gold_dir, f"{location_id}_gold.parquet"))
            save_object(self.config.preprocessor_file_path, preprocessor)
            metadata = {
                "scale_columns": SCALE_COLUMNS,
                "scaler_means": preprocessor.named_steps["scaler"].mean_.tolist(),
                "scaler_scales": preprocessor.named_steps["scaler"].scale_.tolist(),
                "fit_max_time": str(pd.to_datetime(train_df["time"], utc=True).max()),
                "train_split_end": str(train_end),
            }
            config_hash = hash_config(metadata)
            write_json_file(self.config.feature_metadata_file_path, {**metadata, "config_hash": config_hash})
            logger.info("transformation complete", extra={"ctx_train_end": str(train_end)})
            return DataTransformationArtifact(
                gold_dir=self.config.gold_dir,
                preprocessor_file_path=self.config.preprocessor_file_path,
                feature_metadata_file_path=self.config.feature_metadata_file_path,
                config_hash=config_hash,
                train_split_end=str(train_end),
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/feature_engineering.py"] = r'''
import os
import sys

import numpy as np
import pandas as pd

from atmosiq.db.models import FeatureVersion
from atmosiq.entity.artifact_entity import DataTransformationArtifact, FeatureEngineeringArtifact
from atmosiq.entity.config_entity import FeatureEngineeringConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.leakage_guard import LeakageGuard
from atmosiq.utils.main_utils.utils import hash_config, read_parquet, save_parquet

logger = logging.getLogger("atmosiq.components.feature_engineering")

TEMP_LAGS = [1, 3, 6, 12, 24, 48]


class FeatureEngineering:
    def __init__(self, data_transformation_artifact, config, session=None):
        try:
            self.transformation_artifact = data_transformation_artifact
            self.config = config
            self.session = session
            self.guard = LeakageGuard()
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _time_features(self, df):
        t = pd.to_datetime(df["time"], utc=True)
        df = df.copy()
        df["hour"] = t.dt.hour
        df["day"] = t.dt.day
        df["day_of_week"] = t.dt.dayofweek
        df["day_of_year"] = t.dt.dayofyear
        df["week"] = t.dt.isocalendar().week.astype(int)
        df["month"] = t.dt.month
        df["season"] = (t.dt.month % 12 // 3) + 1
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
        df["day_of_year_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
        df["day_of_year_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)
        return df

    def _lag_rolling_features(self, df):
        df = df.copy()
        temp = df["temperature_2m"]
        for lag in TEMP_LAGS:
            df[f"temperature_lag_{lag}"] = temp.shift(lag)
        df["humidity_lag_24"] = df["relative_humidity_2m"].shift(24)
        df["pressure_lag_24"] = df["pressure_msl"].shift(24)
        df["wind_lag_24"] = df["wind_speed_10m"].shift(24)
        for window in (3, 6, 24):
            df[f"temperature_mean_{window}h"] = temp.shift(1).rolling(window).mean()
        for window in (6, 24):
            df[f"temperature_std_{window}h"] = temp.shift(1).rolling(window).std()
            df[f"humidity_mean_{window}h"] = df["relative_humidity_2m"].shift(1).rolling(window).mean()
            df[f"wind_mean_{window}h"] = df["wind_speed_10m"].shift(1).rolling(window).mean()
        df["pressure_change_3h"] = df["pressure_msl"] - df["pressure_msl"].shift(3)
        df["pressure_change_6h"] = df["pressure_msl"] - df["pressure_msl"].shift(6)
        df["pressure_tendency"] = df["pressure_msl"] - df["pressure_msl"].shift(1)
        return df

    def _physical_features(self, df):
        df = df.copy()
        df["dew_point_depression"] = df["temperature_2m"] - df["dew_point_2m"]
        df["apparent_temperature_difference"] = df["apparent_temperature"] - df["temperature_2m"]
        df["wind_direction_sin"] = np.sin(np.deg2rad(df["wind_direction_10m"]))
        df["wind_direction_cos"] = np.cos(np.deg2rad(df["wind_direction_10m"]))
        return df

    def _provider_forecast_features(self, df, forecast_path):
        if not os.path.exists(forecast_path):
            return df
        fc = read_parquet(forecast_path)
        keep = ["issue_time", "valid_time", "temperature_2m", "precipitation", "wind_speed_10m", "relative_humidity_2m", "precipitation_probability"]
        fc = fc[[c for c in keep if c in fc.columns]].rename(columns={
            "temperature_2m": "provider_temperature_forecast",
            "precipitation": "provider_precipitation_forecast",
            "wind_speed_10m": "provider_wind_forecast",
            "relative_humidity_2m": "provider_humidity_forecast",
            "precipitation_probability": "provider_precip_probability_forecast",
        })
        fc["issue_time"] = pd.to_datetime(fc["issue_time"], utc=True)
        fc["valid_time"] = pd.to_datetime(fc["valid_time"], utc=True)
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"], utc=True)
        merged = pd.merge_asof(df.sort_values("time"), fc.sort_values("valid_time"), left_on="time", right_on="valid_time", direction="backward")
        merged = merged[merged["issue_time"].isna() | (merged["issue_time"] <= merged["time"])]
        merged["provider_forecast_lead_time"] = (merged["valid_time"] - merged["issue_time"]).dt.total_seconds() / 3600
        merged["forecast_issue_time"] = merged["issue_time"]
        merged = merged.drop(columns=["issue_time", "valid_time"])
        err = merged.get("provider_temperature_forecast", pd.Series(dtype=float)) - merged["temperature_2m"]
        merged["recent_provider_bias"] = err.shift(1).rolling(24).mean()
        merged["recent_provider_mae"] = err.abs().shift(1).rolling(24).mean()
        merged["recent_provider_error"] = err.shift(1)
        return merged

    def initiate_feature_engineering(self):
        try:
            feature_columns = []
            forecast_root = os.path.normpath(os.path.join(self.transformation_artifact.gold_dir, "..", "..", "data_ingestion", "forecasts"))
            for file_name in sorted(os.listdir(self.transformation_artifact.gold_dir)):
                if not file_name.endswith("_gold.parquet"):
                    continue
                location_id = file_name.replace("_gold.parquet", "")
                df = read_parquet(os.path.join(self.transformation_artifact.gold_dir, file_name))
                df = self._time_features(df)
                df = self._lag_rolling_features(df)
                df = self._physical_features(df)
                df = self._provider_forecast_features(df, os.path.join(forecast_root, f"{location_id}_forecast.parquet"))
                self.guard.assert_lag_columns_causal(df, "time")
                self.guard.assert_forecast_features_causal(df)
                feature_columns = [c for c in df.columns if c not in ("time", "location_id")]
                save_parquet(df, os.path.join(self.config.features_dir, f"{location_id}_features.parquet"))
            version_id = hash_config({"columns": feature_columns, "hash": self.transformation_artifact.config_hash})[:16]
            if self.session is not None:
                self.session.add(FeatureVersion(id=f"feat_{version_id}", feature_columns={"columns": feature_columns}, config_hash=self.transformation_artifact.config_hash))
                self.session.commit()
            logger.info("feature engineering complete", extra={"ctx_n_features": len(feature_columns)})
            return FeatureEngineeringArtifact(
                features_dir=self.config.features_dir,
                feature_version_id=f"feat_{version_id}",
                feature_columns=feature_columns,
                leakage_check_passed=True,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/dataset_creation.py"] = r'''
import os
import sys

import pandas as pd

from atmosiq.db.models import DatasetVersion
from atmosiq.entity.artifact_entity import DatasetCreationArtifact, FeatureEngineeringArtifact
from atmosiq.entity.config_entity import DatasetCreationConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.leakage_guard import LeakageGuard
from atmosiq.utils.main_utils.utils import hash_config, read_parquet, save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.dataset_creation")

TASK_TARGETS = {
    "temperature": [1, 3, 6, 12, 24, 48, 72],
    "precipitation_amount": [1, 3, 6, 24],
    "rain_occurrence": [1, 3, 6, 24],
    "precipitation_probability": [1, 3, 6, 24],
    "wind_speed": [1, 6, 24],
}
TARGET_SOURCE = {
    "temperature": "temperature_2m",
    "precipitation_amount": "precipitation",
    "rain_occurrence": "precipitation",
    "precipitation_probability": "precipitation_probability",
    "wind_speed": "wind_speed_10m",
}


class DatasetCreation:
    def __init__(self, feature_artifact, config, session=None):
        try:
            self.feature_artifact = feature_artifact
            self.config = config
            self.session = session
            self.guard = LeakageGuard()
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _build_targets(self, df):
        df = df.copy()
        threshold = self.config.app.raw["rain"]["occurrence_threshold_mm"]
        for task, horizons in TASK_TARGETS.items():
            source = df[TARGET_SOURCE[task]]
            for horizon in horizons:
                shifted = source.shift(-horizon)
                if task == "rain_occurrence":
                    shifted = (shifted > threshold).astype(float)
                df[f"target_{task}_{horizon}h"] = shifted
        return df

    def initiate_dataset_creation(self):
        try:
            frames = []
            for file_name in sorted(os.listdir(self.feature_artifact.features_dir)):
                if file_name.endswith("_features.parquet"):
                    frames.append(read_parquet(os.path.join(self.feature_artifact.features_dir, file_name)))
            df = pd.concat(frames, ignore_index=True).sort_values("time").reset_index(drop=True)
            df = self._build_targets(df)
            times = pd.to_datetime(df["time"], utc=True)
            splits = self.config.app.splits
            boundaries = times.quantile([splits["train"], splits["train"] + splits["validation"]])
            train_end, val_end = boundaries.iloc[0], boundaries.iloc[1]
            train = df[times <= train_end]
            validation = df[(times > train_end) & (times <= val_end)]
            test = df[times > val_end]
            for name, part in [("train", train), ("validation", validation), ("test", test)]:
                save_parquet(part, os.path.join(self.config.dataset_dir, f"{name}.parquet"))
            manifest = {
                "feature_version_id": self.feature_artifact.feature_version_id,
                "split_boundaries": {"train_end": str(train_end), "validation_end": str(val_end)},
                "row_counts": {"train": len(train), "validation": len(validation), "test": len(test)},
                "tasks": TASK_TARGETS,
                "feature_columns": self.feature_artifact.feature_columns,
                "split_policy": "chronological",
            }
            version_id = hash_config(manifest)[:16]
            manifest["dataset_version_id"] = f"ds_{version_id}"
            write_json_file(self.config.manifest_file_path, manifest)
            if self.session is not None:
                self.session.add(DatasetVersion(
                    id=f"ds_{version_id}", dataset_dir=self.config.dataset_dir,
                    split_boundaries=manifest["split_boundaries"], row_counts=manifest["row_counts"], content_hash=version_id,
                ))
                self.session.commit()
            logger.info("dataset created", extra={"ctx_version": f"ds_{version_id}"})
            return DatasetCreationArtifact(
                dataset_dir=self.config.dataset_dir,
                manifest_file_path=self.config.manifest_file_path,
                dataset_version_id=f"ds_{version_id}",
                train_rows=len(train),
                validation_rows=len(validation),
                test_rows=len(test),
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/baseline_trainer.py"] = r'''
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
'''

W["src/atmosiq/components/model_trainer.py"] = r'''
import os
import platform
import sys
import time
import uuid

import pandas as pd

from atmosiq.db.models import TrainingRun
from atmosiq.entity.artifact_entity import DatasetCreationArtifact, FeatureEngineeringArtifact, HyperparameterTunerArtifact, ModelTrainerArtifact
from atmosiq.entity.config_entity import ModelTrainerConfig
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
}


def feature_columns_for(df):
    cols = []
    for c in df.columns:
        if c in ("time", "location_id") or c.startswith("target_") or c.startswith("forecast_issue_time"):
            continue
        if c in FEATURE_EXACT or c.startswith(FEATURE_TOKENS) or c.startswith("provider_"):
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
            tasks = [("temperature", h, "regression") for h in self.config.app.horizons]
            tasks += [("precipitation_amount", h, "regression") for h in (1, 3, 6, 24)]
            tasks += [("wind_speed", h, "regression") for h in (1, 6, 24)]
            tasks += [("rain_occurrence", h, "classification") for h in (1, 3, 6, 24)]
            for task, horizon, kind in tasks:
                target_col = f"target_{task}_{horizon}h"
                tr = train.dropna(subset=[target_col] + [f for f in features if f in train.columns])
                va = validation.dropna(subset=[target_col] + [f for f in features if f in validation.columns])
                if tr.empty or va.empty:
                    continue
                X_tr, y_tr = tr[features].to_numpy(), tr[target_col].to_numpy()
                X_va, y_va = va[features].to_numpy(), va[target_col].to_numpy()
                model_names = self.config.rain_classifiers if kind == "classification" else self.config.classical_models
                for name in model_names:
                    started = time.monotonic()
                    params = best_params.get(f"{name}@{task}@{horizon}", {})
                    model = ModelFactory.create(name, task, params)
                    model.fit(X_tr, y_tr)
                    pred = model.predict(X_va)
                    if kind == "classification":
                        proba = model.predict_proba(X_va)
                        val_metrics = {
                            "accuracy": metric.accuracy(y_va, pred), "precision": metric.precision(y_va, pred),
                            "recall": metric.recall(y_va, pred), "f1": metric.f1(y_va, pred),
                            "roc_auc": metric.roc_auc(y_va, proba), "pr_auc": metric.pr_auc(y_va, proba),
                            "brier": metric.brier_score(y_va, proba), "log_loss": metric.log_loss(y_va, proba),
                        }
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
'''

W["src/atmosiq/components/hyperparameter_tuner.py"] = r'''
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
'''

W["src/atmosiq/components/deep/__init__.py"] = r'''
"""Deep learning subpackage."""
'''

W["src/atmosiq/components/deep/models.py"] = r'''
import math

import torch
from torch import nn


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, : x.size(1)]


class _SequenceHead(nn.Module):
    def __init__(self, d_model, hidden, out_dim, dropout):
        super().__init__()
        self.head = nn.Sequential(
            nn.LayerNorm(d_model), nn.Linear(d_model, hidden), nn.GELU(),
            nn.Dropout(dropout), nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.head(x[:, -1])


class LSTMModel(nn.Module):
    def __init__(self, in_dim, d_model=64, layers=2, out_dim=1, dropout=0.1):
        super().__init__()
        self.proj = nn.Linear(in_dim, d_model)
        self.rnn = nn.LSTM(d_model, d_model, num_layers=layers, batch_first=True, dropout=dropout)
        self.head = _SequenceHead(d_model, d_model, out_dim, dropout)

    def forward(self, x):
        return self.head(self.rnn(self.proj(x))[0])


class GRUModel(nn.Module):
    def __init__(self, in_dim, d_model=64, layers=2, out_dim=1, dropout=0.1):
        super().__init__()
        self.proj = nn.Linear(in_dim, d_model)
        self.rnn = nn.GRU(d_model, d_model, num_layers=layers, batch_first=True, dropout=dropout)
        self.head = _SequenceHead(d_model, d_model, out_dim, dropout)

    def forward(self, x):
        return self.head(self.rnn(self.proj(x))[0])


class TCNBlock(nn.Module):
    def __init__(self, channels, kernel, dilation, dropout):
        super().__init__()
        padding = (kernel - 1) * dilation
        self.conv1 = nn.utils.parametrizations.weight_norm(nn.Conv1d(channels, channels, kernel, padding=padding, dilation=dilation))
        self.conv2 = nn.utils.parametrizations.weight_norm(nn.Conv1d(channels, channels, kernel, padding=padding, dilation=dilation))
        self.drop = nn.Dropout(dropout)
        self.act = nn.GELU()
        self.chop = padding

    def forward(self, x):
        out = self.act(self.drop(self.act(self.drop(self.conv1(x)[:, :, self.chop:]))))
        out = self.conv2(out)[:, :, self.chop:]
        return self.drop(out) + x


class TCNModel(nn.Module):
    def __init__(self, in_dim, d_model=64, levels=4, kernel=3, out_dim=1, dropout=0.1):
        super().__init__()
        self.proj = nn.Linear(in_dim, d_model)
        self.blocks = nn.Sequential(*[TCNBlock(d_model, kernel, 2 ** i, dropout) for i in range(levels)])
        self.head = _SequenceHead(d_model, d_model, out_dim, dropout)

    def forward(self, x):
        h = self.proj(x).transpose(1, 2)
        return self.head(self.blocks(h).transpose(1, 2))


class WeatherTransformer(nn.Module):
    def __init__(self, in_dim, d_model=64, n_heads=4, layers=2, ffn_dim=128, out_dim=1, dropout=0.1, context_length=48):
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(f"d_model {d_model} must be divisible by n_heads {n_heads}")
        self.proj = nn.Linear(in_dim, d_model)
        self.pos = PositionalEncoding(d_model, context_length + 1)
        encoder_layer = nn.TransformerEncoderLayer(d_model, n_heads, ffn_dim, dropout, batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, layers)
        self.head = _SequenceHead(d_model, ffn_dim, out_dim, dropout)

    def forward(self, x):
        h = self.pos(self.proj(x))
        return self.head(self.encoder(h))


def build_model(name, in_dim, cfg):
    if name == "lstm":
        return LSTMModel(in_dim, cfg.get("d_model", 64), cfg.get("layers", 2), dropout=cfg.get("dropout", 0.1))
    if name == "gru":
        return GRUModel(in_dim, cfg.get("d_model", 64), cfg.get("layers", 2), dropout=cfg.get("dropout", 0.1))
    if name == "tcn":
        return TCNModel(in_dim, cfg.get("d_model", 64), cfg.get("levels", 4), dropout=cfg.get("dropout", 0.1))
    if name == "transformer":
        return WeatherTransformer(in_dim, cfg.get("d_model", 64), cfg.get("heads", 4), cfg.get("layers", 2), cfg.get("ffn_dim", 128), dropout=cfg.get("dropout", 0.1), context_length=cfg.get("context_length", 48))
    raise ValueError(f"Unknown deep model {name}")
'''

W["src/atmosiq/components/deep/trainer.py"] = r'''
import os
import sys
import time

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from atmosiq.components.deep.models import build_model
from atmosiq.components.model_trainer import feature_columns_for
from atmosiq.entity.artifact_entity import DatasetCreationArtifact, ModelTrainerArtifact
from atmosiq.entity.config_entity import DeepTrainerConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import read_parquet, seed_everything
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.deep_trainer")


class WeatherSequenceDataset(Dataset):
    def __init__(self, features, targets, seq_len):
        self.features = torch.tensor(features, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.float32)
        self.seq_len = seq_len

    def __len__(self):
        return max(0, len(self.features) - self.seq_len)

    def __getitem__(self, idx):
        return self.features[idx : idx + self.seq_len], self.targets[idx + self.seq_len - 1]


class DeepTrainer:
    def __init__(self, dataset_artifact, config, model_names=None):
        try:
            self.dataset_artifact = dataset_artifact
            self.config = config
            self.model_names = model_names or ["lstm", "gru", "tcn", "transformer"]
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _loop(self, model, loader, optimizer=None, scheduler=None):
        training = optimizer is not None
        model.train(training)
        loss_fn = torch.nn.HuberLoss()
        total, count = 0.0, 0
        for X, y in loader:
            X, y = X.to(self.device), y.to(self.device)
            if training:
                optimizer.zero_grad()
            pred = model(X).squeeze(-1)
            loss = loss_fn(pred, y)
            if training:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
            total += loss.item() * len(y)
            count += len(y)
        return total / max(count, 1)

    def initiate_deep_training(self, horizon=24):
        try:
            seed_everything(42)
            train = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "train.parquet"))
            validation = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "validation.parquet"))
            target_col = f"target_temperature_{horizon}h"
            features = feature_columns_for(train)
            tr = train.dropna(subset=[target_col] + [f for f in features if f in train.columns])
            va = validation.dropna(subset=[target_col] + [f for f in features if f in validation.columns])
            if tr.empty or va.empty:
                return []
            X_tr, y_tr = tr[features].to_numpy(dtype=np.float32), tr[target_col].to_numpy()
            X_va, y_va = va[features].to_numpy(dtype=np.float32), va[target_col].to_numpy()
            mu, sd = X_tr.mean(0), X_tr.std(0) + 1e-8
            X_tr, X_va = (X_tr - mu) / sd, (X_va - mu) / sd
            train_loader = DataLoader(WeatherSequenceDataset(X_tr, y_tr, self.config.sequence_length), batch_size=self.config.batch_size, shuffle=False)
            val_loader = DataLoader(WeatherSequenceDataset(X_va, y_va, self.config.sequence_length), batch_size=self.config.batch_size)
            artifacts = []
            for name in self.model_names:
                model = build_model(name, X_tr.shape[1], {"context_length": self.config.sequence_length}).to(self.device)
                optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
                scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, self.config.epochs * max(len(train_loader), 1)))
                best_val, patience_left, best_state = float("inf"), self.config.patience, None
                for epoch in range(self.config.epochs):
                    self._loop(model, train_loader, optimizer, scheduler)
                    val_loss = self._loop(model, val_loader)
                    if val_loss < best_val - 1e-4:
                        best_val, best_state = val_loss, {k: v.cpu().clone() for k, v in model.state_dict().items()}
                        patience_left = self.config.patience
                    else:
                        patience_left -= 1
                        if patience_left <= 0:
                            logger.info("early stopping", extra={"ctx_model": name, "ctx_epoch": epoch})
                            break
                if best_state is not None:
                    model.load_state_dict(best_state)
                model.eval()
                preds = []
                with torch.no_grad():
                    for X, _ in val_loader:
                        preds.append(model(X.to(self.device)).squeeze(-1).cpu().numpy())
                preds = np.concatenate(preds) if preds else np.array([])
                y_eval = y_va[self.config.sequence_length :]
                val_metrics = {"mae": metric.mae(y_eval, preds), "rmse": metric.rmse(y_eval, preds)} if len(preds) else {"mae": float("nan"), "rmse": float("nan")}
                path = os.path.join(self.config.deep_dir, f"{name}_{horizon}h.pt")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                torch.save({"state": model.state_dict(), "config": {"name": name, "in_dim": int(X_tr.shape[1])}, "scaler": (mu.tolist(), sd.tolist()), "features": features}, path)
                artifacts.append(ModelTrainerArtifact(
                    trained_model_file_path=path, model_name=name, task="temperature", horizon_hours=horizon,
                    train_metrics={"epochs": self.config.epochs}, validation_metrics=val_metrics, training_run_id=f"deep_{name}_{horizon}h",
                ))
            logger.info("deep training complete", extra={"ctx_models": len(artifacts)})
            return artifacts
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/components/quantile_models.py"] = r'''
import numpy as np

from atmosiq.utils.ml_utils.model.factory import ModelFactory


class QuantileEnsemble:
    def __init__(self, base="lightgbm", quantiles=(0.1, 0.5, 0.9)):
        self.base = base
        self.quantiles = quantiles
        self.models = []

    def fit(self, X, y):
        self.models = []
        for q in self.quantiles:
            if self.base == "lightgbm":
                params = {"objective": "quantile", "alpha": q}
            else:
                params = {"objective": "reg:quantileerror", "quantile_alpha": q}
            model = ModelFactory.create(self.base, "regression", params)
            model.fit(X, y)
            self.models.append(model)
        return self

    def predict_quantiles(self, X):
        return np.column_stack([m.predict(X) for m in self.models])
'''

W["src/atmosiq/components/model_evaluation.py"] = r'''
import os
import sys

import numpy as np
import pandas as pd

from atmosiq.components.model_trainer import feature_columns_for
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
            usable = test.dropna(subset=[target_col] + [f for f in features if f in test.columns])
            if usable.empty:
                continue
            X = usable[features].to_numpy()
            y = usable[target_col].to_numpy()
            blob = load_object(artifact.trained_model_file_path)
            estimator = blob["estimator"] if isinstance(blob, dict) else blob
            pred = estimator.predict(X)
            base = baseline_df[(baseline_df["model"] == "persistence") & (baseline_df["horizon"] == artifact.horizon_hours)]
            baseline_pred = np.full(len(y), base["prediction"].mean()) if not base.empty else y
            row = {
                "model": artifact.model_name, "task": artifact.task, "horizon": artifact.horizon_hours,
                "mae": metric.mae(y, pred), "rmse": metric.rmse(y, pred),
                "mase": metric.mase(y, pred), "skill_vs_persistence": metric.skill_score(y, pred, baseline_pred),
            }
            if artifact.task == "rain_occurrence" and hasattr(estimator, "predict_proba"):
                proba = estimator.predict_proba(X)[:, 1]
                row.update({"pr_auc": metric.pr_auc(y, proba), "brier": metric.brier_score(y, proba), "calibration": metric.calibration_error(y, proba)})
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
            row_passed = all(checks.values()) if checks else True
            decisions.append({"model": row["model"], "task": row["task"], "horizon": row["horizon"], "checks": checks, "passed": row_passed})
        passed_any = any(d["passed"] for d in decisions)
        return {"policy": policy, "decisions": decisions, "passed": passed_any}

    def initiate_model_evaluation(self):
        try:
            test = read_parquet(os.path.join(self.dataset_artifact.dataset_dir, "test.parquet"))
            board = self._evaluate_all(test)
            board.sort(key=lambda r: (r["task"], r["horizon"], r["mae"]))
            write_json_file(self.config.leaderboard_file_path, board)
            error_analysis = self._error_analysis(test)
            write_json_file(self.config.error_analysis_file_path, error_analysis)
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
'''

W["src/atmosiq/components/model_pusher.py"] = r'''
import sys
import uuid

from atmosiq.db.models import Deployment, ModelVersion
from atmosiq.db.repositories import ModelRegistryRepository
from atmosiq.entity.artifact_entity import ModelEvaluationArtifact, ModelPusherArtifact, ModelTrainerArtifact
from atmosiq.entity.config_entity import ModelPusherConfig
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
                mlflow.log_metrics({k: v for k, v in artifact.validation_metrics.items() if isinstance(v, (int, float))})
                mlflow.log_artifact(artifact.trained_model_file_path)
        except Exception as e:
            logger.warning(f"mlflow logging skipped: {e}")

    def initiate_model_pusher(self):
        try:
            require_approval = self.config.app.raw["quality_gate"]["require_manual_approval"]
            if not self.evaluation_artifact.gate_passed:
                return ModelPusherArtifact(False, "", "Candidate", "quality gate failed; candidate not registered for promotion")
            chosen = next((a for a in self.trainer_artifacts if f"{a.model_name}@{a.task}@{a.horizon_hours}" == self.evaluation_artifact.champion_candidate), None)
            if chosen is None:
                return ModelPusherArtifact(False, "", "Candidate", "no trainer artifact matched gate candidate")
            self._mlflow_log(chosen)
            version_id = f"mv_{uuid.uuid4().hex[:12]}"
            self.repo.add_version(ModelVersion(
                id=version_id, model_name=chosen.model_name, task=chosen.task, horizon_hours=chosen.horizon_hours,
                stage="Candidate", training_run_id=chosen.training_run_id, artifact_path=chosen.trained_model_file_path, metrics=chosen.validation_metrics,
            ))
            if require_approval and self.approved_by is None:
                return ModelPusherArtifact(False, version_id, "Candidate", "candidate registered; awaiting manual approval")
            return self.promote(version_id)
        except Exception as e:
            raise AtmosIQException(e, sys)

    def promote(self, version_id):
        version = self.session.get(ModelVersion, version_id)
        if version is None:
            raise AtmosIQException(f"unknown model version {version_id}")
        gate = read_json_file(self.evaluation_artifact.gate_file_path)
        decision = next((d for d in gate["decisions"] if f"{d['model']}@{d['task']}@{d['horizon']}" == f"{version.model_name}@{version.task}@{version.horizon_hours}"), None)
        if decision is None or not decision["passed"]:
            return ModelPusherArtifact(False, version_id, version.stage, "challenger failed quality gate; champion unchanged")
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
'''

W["src/atmosiq/components/prediction_service.py"] = r'''
import sys
import time
import uuid

import pandas as pd

from atmosiq.common.timeutils import floor_hour, now_utc
from atmosiq.db.models import ForecastVerification, Prediction
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_prediction_latency_seconds, atmosiq_prediction_total
from atmosiq.observability.tracing import span_ctx
from atmosiq.utils.main_utils.utils import load_object

logger = logging.getLogger("atmosiq.components.prediction_service")


class PredictionService:
    def __init__(self, session):
        self.session = session
        self.repo = MonitoringRepository(session)
        self._cache = {}

    def _load_champion(self, task, horizon_hours, location_id=None):
        from atmosiq.db.models import ModelVersion
        key = (task, horizon_hours, location_id)
        if key in self._cache:
            return self._cache[key]
        query = (
            self.session.query(ModelVersion)
            .filter_by(task=task, horizon_hours=horizon_hours, stage="Champion")
            .order_by(ModelVersion.created_at.desc())
        )
        if location_id is not None:
            query = query.filter(ModelVersion.location_id == location_id)
        version = query.first()
        if version is None:
            raise AtmosIQException(f"No champion for task={task} horizon={horizon_hours}")
        model_blob = load_object(version.artifact_path)
        self._cache[key] = (version, model_blob)
        return self._cache[key]

    def predict(self, task, horizon_hours, features, location_id=None, issue_time=None):
        request_id = str(uuid.uuid4())
        started = time.monotonic()
        with span_ctx("prediction", {"task": task, "horizon": horizon_hours, "request_id": request_id}):
            try:
                version, model_blob = self._load_champion(task, horizon_hours, location_id)
                estimator = model_blob["estimator"] if isinstance(model_blob, dict) else model_blob
                feature_names = getattr(estimator, "feature_names_in_", None) or sorted(features.keys())
                X = [[features.get(f, 0.0) for f in feature_names]]
                prediction = float(estimator.predict(X)[0])
                probability = None
                if task == "rain_occurrence" and hasattr(estimator, "predict_proba"):
                    probability = float(estimator.predict_proba(X)[0][1])
                latency = time.monotonic() - started
                atmosiq_prediction_latency_seconds.labels(task=task, horizon=str(horizon_hours)).observe(latency)
                atmosiq_prediction_total.labels(task=task, horizon=str(horizon_hours), model=version.model_name).inc()
                issue_time = issue_time or floor_hour(now_utc())
                payload = {
                    "location": location_id,
                    "forecast_issue_time": issue_time.isoformat(),
                    "horizon_hours": horizon_hours,
                    "model": version.model_name,
                    "model_version": version.id,
                    "prediction": prediction,
                }
                if probability is not None:
                    payload["rain_probability"] = probability
                self.repo.add_prediction(Prediction(
                    request_id=request_id, model_version_id=version.id, location_id=location_id or "unknown",
                    issue_time=issue_time, valid_time=issue_time + pd.Timedelta(hours=horizon_hours),
                    horizon_hours=horizon_hours, task=task, payload=payload,
                ))
                logger.info("prediction served", extra={"ctx_request_id": request_id, "ctx_model": version.model_name})
                return payload
            except Exception as e:
                raise AtmosIQException(e, sys)

    def verify_forecast(self, model_version_id, location_id, issue_time, valid_time, lead_hours, task, forecast_value, actual_value):
        self.repo.add_verification(ForecastVerification(
            model_version_id=model_version_id, location_id=location_id, issue_time=issue_time,
            valid_time=valid_time, lead_time_hours=lead_hours, task=task,
            forecast_value=forecast_value, actual_value=actual_value, error=forecast_value - actual_value,
        ))
'''

W["src/atmosiq/components/drift_monitor.py"] = r'''
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from atmosiq.common.timeutils import now_utc
from atmosiq.db.models import DriftEvent
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_data_drift_events_total
from atmosiq.utils.main_utils.utils import write_json_file

logger = logging.getLogger("atmosiq.components.drift_monitor")


def compute_psi(reference, current, bins=10):
    reference = reference[~np.isnan(reference)]
    current = current[~np.isnan(current)]
    if len(reference) < 2 or len(current) < 2:
        return float("nan")
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    eps = 1e-6
    ref_frac = (ref_counts + eps) / (ref_counts.sum() + eps * bins)
    cur_frac = (cur_counts + eps) / (cur_counts.sum() + eps * bins)
    return float(np.sum((cur_frac - ref_frac) * np.log(cur_frac / ref_frac)))


class DriftMonitor:
    def __init__(self, session, psi_threshold=0.25, ks_alpha=0.05):
        self.session = session
        self.repo = MonitoringRepository(session)
        self.psi_threshold = psi_threshold
        self.ks_alpha = ks_alpha

    def check_feature(self, feature, reference, current, reference_period, current_period):
        psi = compute_psi(reference, current)
        ks_stat, p_value = ks_2samp(reference, current)
        detected = bool(psi > self.psi_threshold) or bool(p_value < self.ks_alpha)
        event = DriftEvent(
            feature=feature, reference_period=reference_period, current_period=current_period,
            psi=psi, ks_statistic=ks_stat, p_value=p_value, threshold=self.psi_threshold, detected=detected,
        )
        self.repo.add_drift_event(event)
        if detected:
            atmosiq_data_drift_events_total.labels(feature=feature).inc()
            logger.warning("drift detected", extra={"ctx_feature": feature, "ctx_psi": round(psi, 4)})
        return event

    def check_dataframe(self, reference_df, current_df, feature_columns):
        events = []
        reference_period = f"{reference_df['time'].min()}__{reference_df['time'].max()}" if "time" in reference_df else "reference"
        current_period = f"{current_df['time'].min()}__{current_df['time'].max()}" if "time" in current_df else "current"
        for column in feature_columns:
            if column not in reference_df.columns or column not in current_df.columns:
                continue
            events.append(self.check_feature(
                column,
                reference_df[column].to_numpy(dtype=float),
                current_df[column].to_numpy(dtype=float),
                reference_period,
                current_period,
            ))
        return events

    def write_report(self, events, path):
        payload = [
            {
                "feature": e.feature, "psi": e.psi, "ks_statistic": e.ks_statistic, "p_value": e.p_value,
                "threshold": e.threshold, "detected": e.detected,
                "reference_period": e.reference_period, "current_period": e.current_period,
            }
            for e in events
        ]
        write_json_file(path, {"generated_at": now_utc().isoformat(), "events": payload})
'''

W["src/atmosiq/components/performance_monitor.py"] = r'''
import numpy as np
import pandas as pd

from atmosiq.db.models import ForecastVerification, PerformanceEvent
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_model_health, atmosiq_model_performance
from atmosiq.utils.ml_utils.metric import metrics as metric

logger = logging.getLogger("atmosiq.components.performance_monitor")


class PerformanceMonitor:
    def __init__(self, session):
        self.session = session
        self.repo = MonitoringRepository(session)

    def rolling_metrics(self, predictions, window_hours=168):
        df = predictions.sort_values("valid_time").set_index("valid_time")
        recent = df.last(f"{window_hours}h")
        if recent.empty or recent["actual_value"].isna().all():
            return {}
        y = recent["actual_value"].to_numpy()
        p = recent["forecast_value"].to_numpy()
        return {"mae": metric.mae(y, p), "rmse": metric.rmse(y, p), "bias": float(np.mean(p - y)), "window_hours": window_hours, "n": int(len(recent))}

    def verify_by_horizon(self, verifications):
        records = [
            {
                "lead_time_hours": v.lead_time_hours,
                "error": v.error if v.error is not None else (v.forecast_value - v.actual_value if v.forecast_value is not None and v.actual_value is not None else None),
            }
            for v in verifications
        ]
        df = pd.DataFrame(records).dropna(subset=["error"])
        if df.empty:
            return {}
        buckets = [(0, 2), (2, 12), (12, 30), (30, 54), (54, 120)]
        result = {}
        for low, high in buckets:
            sub = df[(df["lead_time_hours"] > low) & (df["lead_time_hours"] <= high)]
            if sub.empty:
                continue
            label = f"{int(np.median(sub['lead_time_hours']))}h"
            result[label] = {
                "mae": float(sub["error"].abs().mean()),
                "rmse": float(np.sqrt((sub["error"] ** 2).mean())),
                "bias": float(sub["error"].mean()),
                "n": int(len(sub)),
            }
        return result

    def record_performance(self, model_version_id, metrics, window_start, window_end):
        self.repo.add_performance_event(PerformanceEvent(model_version_id=model_version_id, window_start=window_start, window_end=window_end, metrics=metrics))
        if "mae" in metrics:
            atmosiq_model_performance.labels(model=model_version_id, task="temperature", metric="mae").set(metrics["mae"])

    def assess_health(self, current_metrics, baseline_mae, tolerance=1.5):
        if not current_metrics or "mae" not in current_metrics:
            return False
        healthy = current_metrics["mae"] <= baseline_mae * tolerance
        atmosiq_model_health.labels(model="champion", task="temperature").set(1.0 if healthy else 0.0)
        return healthy
'''

W["src/atmosiq/components/alert_manager.py"] = r'''
from datetime import timedelta

from atmosiq.common.timeutils import now_utc
from atmosiq.db.models import Alert
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_alerts_active

logger = logging.getLogger("atmosiq.components.alert_manager")

SEVERITY_ORDER = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}


class AlertManager:
    def __init__(self, session, cooldown_minutes=30):
        self.session = session
        self.repo = MonitoringRepository(session)
        self.cooldown = timedelta(minutes=cooldown_minutes)

    def _in_cooldown(self, alert_type, scope):
        latest = self.repo.latest_alert(alert_type, scope)
        if latest is None:
            return False
        last = latest.created_at
        if last.tzinfo is None:
            from datetime import timezone
            last = last.replace(tzinfo=timezone.utc)
        return (now_utc() - last) < self.cooldown

    def raise_alert(self, alert_type, severity, scope, message, recommendation=None):
        if severity not in SEVERITY_ORDER:
            raise AtmosIQException(f"invalid severity {severity}")
        if self._in_cooldown(alert_type, scope):
            logger.info("alert suppressed by cooldown", extra={"ctx_type": alert_type})
            return None
        alert = Alert(alert_type=alert_type, severity=severity, scope=scope, message=message, recommendation=recommendation, status="open")
        self.repo.add_alert(alert)
        atmosiq_alerts_active.labels(severity=severity, alert_type=alert_type).inc()
        logger.warning("alert raised", extra={"ctx_type": alert_type, "ctx_severity": severity})
        return alert

    def resolve_alert(self, alert_id):
        alert = self.session.get(Alert, alert_id)
        if alert is None:
            raise AtmosIQException(f"alert {alert_id} not found")
        alert.status = "resolved"
        self.session.commit()
        atmosiq_alerts_active.labels(severity=alert.severity, alert_type=alert.alert_type).dec()

    def alert_provider_failure(self, provider):
        return self.raise_alert("provider_failure", "CRITICAL", f"provider:{provider}", f"Weather provider {provider} failed", "Switch provider or retry later")

    def alert_stale_data(self, location_id, hours):
        return self.raise_alert("data_stale", "WARNING", f"location:{location_id}", f"Data for {location_id} is {hours:.1f}h stale", "Trigger ingestion")

    def alert_drift(self, feature):
        return self.raise_alert("drift_detected", "WARNING", f"feature:{feature}", f"Drift detected on {feature}", "Run retraining pipeline")

    def alert_model_degradation(self, model_version_id, mae, baseline):
        return self.raise_alert("model_degradation", "CRITICAL", f"model:{model_version_id}", f"MAE {mae:.3f} exceeds baseline {baseline:.3f}", "Rollback to previous champion")
'''

W["src/atmosiq/components/retraining_service.py"] = r'''
from atmosiq.components.alert_manager import AlertManager
from atmosiq.db.repositories import MonitoringRepository
from atmosiq.logging.logger import logging
from atmosiq.pipeline.training_pipeline import TrainingPipeline

logger = logging.getLogger("atmosiq.components.retraining_service")


class RetrainingService:
    def __init__(self, session, drift_threshold_events=2):
        self.session = session
        self.repo = MonitoringRepository(session)
        self.drift_threshold_events = drift_threshold_events
        self.alerts = AlertManager(session)

    def should_retrain(self, drift_events_recent, performance_degraded):
        confirmed_drift = len([e for e in drift_events_recent if e.detected]) >= self.drift_threshold_events
        if confirmed_drift and performance_degraded:
            return True, "drift+degradation"
        if performance_degraded:
            return True, "performance_degradation"
        if confirmed_drift:
            return True, "confirmed_drift"
        return False, "no_trigger"

    def run_retraining(self, trigger_reason, approved_by=None):
        logger.info("retraining triggered", extra={"ctx_reason": trigger_reason})
        pipeline = TrainingPipeline(session=self.session, approved_by=approved_by, deep=False, tune=False)
        artifacts = pipeline.run()
        pusher = artifacts["pusher"]
        if pusher.stage == "Champion":
            logger.info("retraining promoted champion", extra={"ctx_version": pusher.model_version_id})
        else:
            logger.info("retraining candidate not promoted", extra={"ctx_stage": pusher.stage})
        return {"trigger_reason": trigger_reason, "pusher": pusher}
'''

W["src/atmosiq/pipeline/__init__.py"] = r'''
"""Pipeline package."""
'''

W["src/atmosiq/pipeline/training_pipeline.py"] = r'''
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
from atmosiq.entity.config_entity import (
    BaselineTrainerConfig, DataIngestionConfig, DataTransformationConfig, DataValidationConfig,
    DatasetCreationConfig, DeepTrainerConfig, FeatureEngineeringConfig, HyperparameterTunerConfig,
    ModelEvaluationConfig, ModelPusherConfig, ModelTrainerConfig, TrainingPipelineConfig,
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
'''

W["src/atmosiq/pipeline/monitoring_pipeline.py"] = r'''
import sys

import pandas as pd

from atmosiq.common.timeutils import now_utc
from atmosiq.components.alert_manager import AlertManager
from atmosiq.components.drift_monitor import DriftMonitor
from atmosiq.components.performance_monitor import PerformanceMonitor
from atmosiq.db.models import ForecastVerification
from atmosiq.db.repositories import MonitoringRepository, ObservationRepository
from atmosiq.entity.config_entity import AppConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.tracing import span_ctx

logger = logging.getLogger("atmosiq.pipeline.monitoring_pipeline")


class MonitoringPipeline:
    def __init__(self, session):
        self.session = session
        self.app = AppConfig()
        self.repo = MonitoringRepository(session)
        self.drift_monitor = DriftMonitor(session, self.app.raw["drift"]["psi_threshold"], self.app.raw["drift"]["ks_alpha"])
        self.performance_monitor = PerformanceMonitor(session)
        self.alert_manager = AlertManager(session, self.app.raw["alerts"]["cooldown_minutes"])

    def _fetch_reference_current(self, location_id, lookback_hours=720, window_hours=168):
        obs = ObservationRepository(self.session).observations_df(location_id, "open_meteo")
        if obs.empty:
            return None, None
        obs = obs.sort_values("time")
        current = obs.tail(window_hours)
        reference = obs.iloc[:-window_hours] if len(obs) > window_hours else obs.head(max(1, len(obs) - window_hours))
        return reference, current

    def run_drift_checks(self, location_ids, features):
        events = []
        with span_ctx("drift_check"):
            for location_id in location_ids:
                reference, current = self._fetch_reference_current(location_id)
                if reference is None or current is None:
                    continue
                events += self.drift_monitor.check_dataframe(reference, current, features)
        return events

    def run_performance_checks(self):
        with span_ctx("performance_check"):
            verifications = self.session.query(ForecastVerification).order_by(ForecastVerification.valid_time.desc()).limit(5000).all()
            by_horizon = self.performance_monitor.verify_by_horizon(verifications)
            if verifications:
                df = pd.DataFrame([
                    {"valid_time": v.valid_time, "forecast_value": v.forecast_value, "actual_value": v.actual_value}
                    for v in verifications
                ])
                rolling = self.performance_monitor.rolling_metrics(df)
                return {"by_horizon": by_horizon, "rolling": rolling}
            return {"by_horizon": by_horizon, "rolling": {}}

    def run_cycle(self):
        try:
            features = ["temperature_2m", "relative_humidity_2m", "pressure_msl", "wind_speed_10m"]
            location_ids = [loc["id"] for loc in self.app.locations]
            drift_events = self.run_drift_checks(location_ids, features)
            performance = self.run_performance_checks()
            detected = [e for e in drift_events if e.detected]
            for event in detected:
                self.alert_manager.alert_drift(event.feature)
            for location_id in location_ids:
                latest = ObservationRepository(self.session).latest_observation_time(location_id, "open_meteo")
                if latest is not None:
                    last = latest if latest.tzinfo else latest.replace(tzinfo=now_utc().tzinfo)
                    age_hours = (now_utc() - last).total_seconds() / 3600
                    if age_hours > 24:
                        self.alert_manager.alert_stale_data(location_id, age_hours)
            return {"drift_events": len(drift_events), "detected": len(detected), "performance": performance}
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/observability/__init__.py"] = r'''
"""Observability: Prometheus + tracing."""
'''

W["src/atmosiq/observability/prometheus.py"] = r'''
from prometheus_client import Counter, Gauge, Histogram

atmosiq_requests_total = Counter("atmosiq_requests_total", "Total API requests", ["endpoint", "method", "status"])
atmosiq_request_latency_seconds = Histogram("atmosiq_request_latency_seconds", "API request latency", ["endpoint"], buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5))
atmosiq_prediction_total = Counter("atmosiq_prediction_total", "Total model predictions", ["task", "horizon", "model"])
atmosiq_prediction_latency_seconds = Histogram("atmosiq_prediction_latency_seconds", "Prediction latency", ["task", "horizon"])
atmosiq_pipeline_runs_total = Counter("atmosiq_pipeline_runs_total", "Total pipeline runs", ["pipeline", "status"])
atmosiq_training_runs_total = Counter("atmosiq_training_runs_total", "Total training runs", ["model", "task"])
atmosiq_validation_failures_total = Counter("atmosiq_validation_failures_total", "Total validation failures", ["check"])
atmosiq_data_drift_events_total = Counter("atmosiq_data_drift_events_total", "Total drift events", ["feature"])
atmosiq_model_performance = Gauge("atmosiq_model_performance", "Current model performance metric", ["model", "task", "metric"])
atmosiq_model_health = Gauge("atmosiq_model_health", "Model health", ["model", "task"])
atmosiq_alerts_active = Gauge("atmosiq_alerts_active", "Active alerts", ["severity", "alert_type"])
'''

W["src/atmosiq/observability/tracing.py"] = r'''
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracing(service_name="atmosiq", exporter=None):
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    if exporter is not None:
        provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


def get_tracer(service_name="atmosiq"):
    return trace.get_tracer(service_name)


class span_ctx:
    def __init__(self, name, attributes=None):
        self.name = name
        self.attributes = attributes or {}
        self.tracer = get_tracer()

    def __enter__(self):
        self.span = self.tracer.start_span(self.name)
        for k, v in self.attributes.items():
            self.span.set_attribute(k, str(v))
        return self.span

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.span.record_exception(exc)
            self.span.set_status(trace.StatusCode.ERROR, str(exc))
        self.span.end()
        return False
'''

W["src/atmosiq/api/__init__.py"] = r'''
"""API package."""
'''

W["src/atmosiq/api/schemas.py"] = r'''
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str


class LocationOut(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    timezone: str


class CurrentWeatherOut(BaseModel):
    location: str
    observation_time: str
    temperature_2m: float | None = None
    apparent_temperature: float | None = None
    relative_humidity_2m: float | None = None
    wind_speed_10m: float | None = None
    pressure_msl: float | None = None
    visibility: float | None = None
    weather_code: int | None = None


class HourlyForecastOut(BaseModel):
    location: str
    times: list[str]
    temperature_2m: list[float | None]
    precipitation: list[float | None]
    precipitation_probability: list[float | None]
    wind_speed_10m: list[float | None]


class DailyForecastOut(BaseModel):
    location: str
    dates: list[str]
    temperature_max: list[float | None]
    temperature_min: list[float | None]
    precipitation_sum: list[float | None]
    precipitation_probability_max: list[float | None]
    wind_speed_max: list[float | None]


class PredictTemperatureRequest(BaseModel):
    location: str
    horizon_hours: int = Field(default=24, ge=1, le=72)
    features: dict


class TemperaturePredictionOut(BaseModel):
    location: str
    forecast_issue_time: str
    horizon_hours: int
    model: str
    model_version: str
    prediction: float
    lower: float | None = None
    upper: float | None = None


class PredictRainRequest(BaseModel):
    location: str
    horizon_hours: int = Field(default=24, ge=1, le=72)
    features: dict


class RainPredictionOut(BaseModel):
    location: str
    forecast_issue_time: str
    horizon_hours: int
    rain_probability: float | None = None
    rainfall_mm: float | None = None
    category: str
    model: str
    model_version: str


class PredictWindRequest(BaseModel):
    location: str
    horizon_hours: int = Field(default=24, ge=1, le=72)
    features: dict


class WindPredictionOut(BaseModel):
    location: str
    forecast_issue_time: str
    horizon_hours: int
    wind_speed: float
    model: str
    model_version: str


class ModelOut(BaseModel):
    id: str
    model_name: str
    task: str
    horizon_hours: int
    stage: str
    location_id: str | None = None


class MonitoringSummaryOut(BaseModel):
    active_alerts: int
    drift_events: int
    performance_events: int
    champion_count: int


class DriftEventOut(BaseModel):
    feature: str
    reference_period: str
    current_period: str
    psi: float | None = None
    ks_statistic: float | None = None
    p_value: float | None = None
    threshold: float
    detected: bool
    timestamp: str
'''

W["src/atmosiq/api/app.py"] = r'''
import os
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text

from atmosiq import __version__
from atmosiq.api import schemas
from atmosiq.db.models import Alert, DriftEvent, Location, ModelVersion, PerformanceEvent
from atmosiq.db.session import get_session
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.observability.prometheus import atmosiq_request_latency_seconds, atmosiq_requests_total
from atmosiq.providers import get_provider

logger = logging.getLogger("atmosiq.api")


@asynccontextmanager
async def lifespan(app):
    app.state.db_session = get_session()
    yield
    app.state.db_session.close()


app = FastAPI(title="AtmosIQ", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AtmosIQException)
async def atmosiq_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"error": "internal_error", "detail": str(exc)[:200]})


@app.middleware("http")
async def instrument(request, call_next):
    import time
    started = time.monotonic()
    response = await call_next(request)
    latency = time.monotonic() - started
    atmosiq_requests_total.labels(endpoint=request.url.path, method=request.method, status=response.status_code).inc()
    atmosiq_request_latency_seconds.labels(endpoint=request.url.path).observe(latency)
    return response


@app.get("/health/live", response_model=schemas.HealthResponse)
def health_live():
    return schemas.HealthResponse(status="ok", version=__version__)


@app.get("/health/ready", response_model=schemas.HealthResponse)
def health_ready(request: Request):
    try:
        request.app.state.db_session.execute(text("SELECT 1"))
        return schemas.HealthResponse(status="ready", version=__version__)
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")


@app.get("/api/v1/locations", response_model=list[schemas.LocationOut])
def list_locations(request: Request):
    session = request.app.state.db_session
    locations = session.query(Location).all()
    return [schemas.LocationOut(id=l.id, name=l.name, latitude=l.latitude, longitude=l.longitude, timezone=l.timezone) for l in locations]


@app.get("/api/v1/weather/current/{location_id}", response_model=schemas.CurrentWeatherOut)
def current_weather(location_id, request: Request):
    from atmosiq.db.repositories import ObservationRepository
    session = request.app.state.db_session
    df = ObservationRepository(session).observations_df(location_id, "open_meteo")
    if df.empty:
        raise HTTPException(status_code=404, detail="no observations for location")
    latest = df.iloc[-1]
    return schemas.CurrentWeatherOut(
        location=location_id,
        observation_time=str(latest["time"]),
        temperature_2m=latest.get("temperature_2m"),
        apparent_temperature=latest.get("apparent_temperature"),
        relative_humidity_2m=latest.get("relative_humidity_2m"),
        wind_speed_10m=latest.get("wind_speed_10m"),
        pressure_msl=latest.get("pressure_msl"),
        visibility=latest.get("visibility"),
        weather_code=int(latest["weather_code"]) if latest.get("weather_code") is not None else None,
    )


@app.get("/api/v1/weather/hourly/{location_id}", response_model=schemas.HourlyForecastOut)
def hourly_weather(location_id, request: Request):
    from atmosiq.db.repositories import ObservationRepository
    session = request.app.state.db_session
    df = ObservationRepository(session).observations_df(location_id, "open_meteo").tail(48)
    if df.empty:
        raise HTTPException(status_code=404, detail="no hourly data")
    return schemas.HourlyForecastOut(
        location=location_id,
        times=df["time"].astype(str).tolist(),
        temperature_2m=[None if pd.isna(v) else float(v) for v in df.get("temperature_2m", [])],
        precipitation=[None if pd.isna(v) else float(v) for v in df.get("precipitation", [])],
        precipitation_probability=[None if pd.isna(v) else float(v) for v in df.get("precipitation_probability", [])],
        wind_speed_10m=[None if pd.isna(v) else float(v) for v in df.get("wind_speed_10m", [])],
    )


@app.get("/api/v1/weather/daily/{location_id}", response_model=schemas.DailyForecastOut)
def daily_weather(location_id, request: Request):
    from atmosiq.db.repositories import ObservationRepository
    session = request.app.state.db_session
    df = ObservationRepository(session).observations_df(location_id, "open_meteo")
    if df.empty:
        raise HTTPException(status_code=404, detail="no daily data")
    df = df.copy()
    df["date"] = df["time"].dt.date.astype(str)
    daily = df.groupby("date").agg(
        temperature_max=("temperature_2m", "max"),
        temperature_min=("temperature_2m", "min"),
        precipitation_sum=("precipitation", "sum"),
        wind_speed_max=("wind_speed_10m", "max"),
    ).reset_index().tail(7)
    return schemas.DailyForecastOut(
        location=location_id,
        dates=daily["date"].tolist(),
        temperature_max=[None if pd.isna(v) else float(v) for v in daily["temperature_max"]],
        temperature_min=[None if pd.isna(v) else float(v) for v in daily["temperature_min"]],
        precipitation_sum=[None if pd.isna(v) else float(v) for v in daily["precipitation_sum"]],
        precipitation_probability_max=[None] * len(daily),
        wind_speed_max=[None if pd.isna(v) else float(v) for v in daily["wind_speed_max"]],
    )


@app.get("/api/v1/forecast/{location_id}")
def provider_forecast(location_id, request: Request):
    session = request.app.state.db_session
    location = session.query(Location).filter_by(id=location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="location not found")
    provider = get_provider("open_meteo", {})
    bundle = provider.fetch_forecast({"id": location.id, "latitude": location.latitude, "longitude": location.longitude})
    return {"location": location_id, "issue_time": bundle.issue_time.isoformat(), "provider": "open_meteo", "hourly": bundle.hourly.to_dict("records")}


@app.post("/api/v1/predict/temperature", response_model=schemas.TemperaturePredictionOut)
def predict_temperature(body, request: Request):
    from atmosiq.components.prediction_service import PredictionService
    service = PredictionService(request.app.state.db_session)
    try:
        result = service.predict("temperature", body.horizon_hours, body.features, body.location)
    except AtmosIQException as e:
        raise HTTPException(status_code=500, detail=str(e))
    return schemas.TemperaturePredictionOut(
        location=body.location, forecast_issue_time=result["forecast_issue_time"], horizon_hours=result["horizon_hours"],
        model=result["model"], model_version=result["model_version"], prediction=result["prediction"],
    )


@app.post("/api/v1/predict/rain", response_model=schemas.RainPredictionOut)
def predict_rain(body, request: Request):
    from atmosiq.components.prediction_service import PredictionService
    service = PredictionService(request.app.state.db_session)
    amount = service.predict("precipitation_amount", body.horizon_hours, body.features, body.location)
    try:
        occ = service.predict("rain_occurrence", body.horizon_hours, body.features, body.location)
        probability = occ.get("rain_probability")
    except AtmosIQException:
        probability = None
    rainfall = amount["prediction"]
    if rainfall >= 7.5:
        category = "heavy"
    elif rainfall >= 2.5:
        category = "moderate"
    elif rainfall >= 0.2:
        category = "light"
    else:
        category = "none"
    return schemas.RainPredictionOut(
        location=body.location, forecast_issue_time=amount["forecast_issue_time"], horizon_hours=amount["horizon_hours"],
        rain_probability=probability, rainfall_mm=rainfall, category=category, model=amount["model"], model_version=amount["model_version"],
    )


@app.post("/api/v1/predict/wind", response_model=schemas.WindPredictionOut)
def predict_wind(body, request: Request):
    from atmosiq.components.prediction_service import PredictionService
    service = PredictionService(request.app.state.db_session)
    result = service.predict("wind_speed", body.horizon_hours, body.features, body.location)
    return schemas.WindPredictionOut(
        location=body.location, forecast_issue_time=result["forecast_issue_time"], horizon_hours=result["horizon_hours"],
        wind_speed=result["prediction"], model=result["model"], model_version=result["model_version"],
    )


@app.get("/api/v1/models", response_model=list[schemas.ModelOut])
def list_models(request: Request):
    session = request.app.state.db_session
    versions = session.query(ModelVersion).order_by(ModelVersion.created_at.desc()).limit(50).all()
    return [schemas.ModelOut(id=v.id, model_name=v.model_name, task=v.task, horizon_hours=v.horizon_hours, stage=v.stage, location_id=v.location_id) for v in versions]


@app.get("/api/v1/models/{model_id}", response_model=schemas.ModelOut)
def get_model(model_id, request: Request):
    session = request.app.state.db_session
    version = session.get(ModelVersion, model_id)
    if version is None:
        raise HTTPException(status_code=404, detail="model not found")
    return schemas.ModelOut(id=version.id, model_name=version.model_name, task=version.task, horizon_hours=version.horizon_hours, stage=version.stage, location_id=version.location_id)


@app.get("/api/v1/monitoring/summary", response_model=schemas.MonitoringSummaryOut)
def monitoring_summary(request: Request):
    session = request.app.state.db_session
    return schemas.MonitoringSummaryOut(
        active_alerts=session.query(Alert).filter_by(status="open").count(),
        drift_events=session.query(DriftEvent).filter_by(detected=True).count(),
        performance_events=session.query(PerformanceEvent).count(),
        champion_count=session.query(ModelVersion).filter_by(stage="Champion").count(),
    )


@app.get("/api/v1/monitoring/drift", response_model=list[schemas.DriftEventOut])
def monitoring_drift(request: Request):
    session = request.app.state.db_session
    events = session.query(DriftEvent).order_by(DriftEvent.created_at.desc()).limit(100).all()
    return [
        schemas.DriftEventOut(
            feature=e.feature, reference_period=e.reference_period, current_period=e.current_period,
            psi=e.psi, ks_statistic=e.ks_statistic, p_value=e.p_value, threshold=e.threshold,
            detected=e.detected, timestamp=str(e.created_at),
        )
        for e in events
    ]


@app.get("/api/v1/monitoring/performance")
def monitoring_performance(request: Request):
    session = request.app.state.db_session
    events = session.query(PerformanceEvent).order_by(PerformanceEvent.created_at.desc()).limit(50).all()
    return [
        {"model_version_id": e.model_version_id, "window_start": str(e.window_start), "window_end": str(e.window_end), "metrics": e.metrics}
        for e in events
    ]


@app.get("/api/v1/alerts")
def list_alerts(request: Request):
    session = request.app.state.db_session
    alerts = session.query(Alert).order_by(Alert.created_at.desc()).limit(100).all()
    return [
        {"id": a.id, "alert_type": a.alert_type, "severity": a.severity, "scope": a.scope, "message": a.message, "recommendation": a.recommendation, "status": a.status, "created_at": str(a.created_at)}
        for a in alerts
    ]


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


FRONTEND_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
'''

W["src/atmosiq/cli.py"] = r'''
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
def predict(task, horizon):
    from atmosiq.components.prediction_service import PredictionService
    from atmosiq.db.session import get_session

    def run():
        session = get_session()
        service = PredictionService(session)
        result = service.predict(task, horizon, {}, None)
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
'''

W["src/atmosiq/worker.py"] = r'''
import os
import time

from atmosiq.db.session import get_session
from atmosiq.logging.logger import logging
from atmosiq.pipeline.monitoring_pipeline import MonitoringPipeline

logger = logging.getLogger("atmosiq.worker")

MONITOR_INTERVAL_SECONDS = int(os.getenv("MONITOR_INTERVAL_SECONDS", "300"))
RETRAIN_INTERVAL_SECONDS = int(os.getenv("RETRAIN_INTERVAL_SECONDS", "86400"))


def main():
    session = get_session()
    last_monitor = 0.0
    last_retrain = 0.0
    logger.info("worker started")
    while True:
        now = time.monotonic()
        if now - last_monitor >= MONITOR_INTERVAL_SECONDS:
            try:
                result = MonitoringPipeline(session).run_cycle()
                logger.info("monitoring cycle", extra={"ctx_result": result})
            except Exception as e:
                logger.error(f"monitoring cycle failed: {e}")
            last_monitor = now
        if now - last_retrain >= RETRAIN_INTERVAL_SECONDS:
            try:
                from atmosiq.components.retraining_service import RetrainingService
                RetrainingService(session).run_retraining("scheduled")
            except Exception as e:
                logger.error(f"retraining failed: {e}")
            last_retrain = now
        time.sleep(10)


if __name__ == "__main__":
    main()
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 2 written: {len(W)} files.")
