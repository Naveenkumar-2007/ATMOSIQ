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
        loc_map = {loc["id"]: loc for loc in self.config.app.locations}
        frames = []
        for file_name in sorted(os.listdir(self.validation_artifact.silver_dir)):
            if file_name.endswith("_hourly.parquet"):
                location_id = file_name.replace("_hourly.parquet", "")
                df = read_parquet(os.path.join(self.validation_artifact.silver_dir, file_name))
                df["location_id"] = location_id
                loc_info = loc_map.get(location_id, {})
                df["latitude"] = float(loc_info.get("latitude", 0.0))
                df["longitude"] = float(loc_info.get("longitude", 0.0))
                df["elevation"] = float(loc_info.get("elevation", 0.0))
                frames.append(df)
        df_all = pd.concat(frames, ignore_index=True).sort_values(["location_id", "time"])
        if "apparent_temperature" in df_all.columns:
            df_all["apparent_temperature"] = df_all["apparent_temperature"].fillna(df_all["temperature_2m"])
        return df_all

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
