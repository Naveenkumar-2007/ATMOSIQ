import os
import sys

import numpy as np
import pandas as pd

from atmosiq.db.models import FeatureVersion
from atmosiq.entity.artifact_entity import FeatureEngineeringArtifact
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.leakage_guard import LeakageGuard
from atmosiq.utils.main_utils.utils import hash_config, read_parquet, save_parquet

logger = logging.getLogger("atmosiq.components.feature_engineering")

TEMP_LAGS = [1, 3, 6, 12, 24, 48]


def _time_features(df):
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


def _lag_rolling_features(df):
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


def _physical_features(df):
    df = df.copy()
    temp = pd.to_numeric(df.get("temperature_2m", pd.Series(dtype=float, index=df.index)), errors="coerce")
    dew = pd.to_numeric(df.get("dew_point_2m", pd.Series(dtype=float, index=df.index)), errors="coerce")
    apparent = pd.to_numeric(df.get("apparent_temperature", temp), errors="coerce").fillna(temp)
    wind_dir = pd.to_numeric(df.get("wind_direction_10m", pd.Series(dtype=float, index=df.index)), errors="coerce").fillna(0)
    df["dew_point_depression"] = temp - dew
    df["apparent_temperature_difference"] = apparent - temp
    df["wind_direction_sin"] = np.sin(np.deg2rad(wind_dir))
    df["wind_direction_cos"] = np.cos(np.deg2rad(wind_dir))
    return df


def _provider_forecast_features(df, forecast_df):
    if forecast_df is None or forecast_df.empty:
        return df
    fc = forecast_df.copy()
    rename = {
        "temperature_2m": "provider_temperature_forecast",
        "precipitation": "provider_precipitation_forecast",
        "wind_speed_10m": "provider_wind_forecast",
        "relative_humidity_2m": "provider_humidity_forecast",
        "precipitation_probability": "provider_precip_probability_forecast",
    }
    keep = ["issue_time", "valid_time"] + [c for c in rename if c in fc.columns]
    fc = fc[keep].rename(columns=rename)
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


def build_features(df, forecast_df=None):
    df = _time_features(df)
    df = _lag_rolling_features(df)
    df = _physical_features(df)
    df = _provider_forecast_features(df, forecast_df)
    return df


class FeatureEngineering:
    def __init__(self, data_transformation_artifact, config, session=None):
        try:
            self.transformation_artifact = data_transformation_artifact
            self.config = config
            self.session = session
            self.guard = LeakageGuard()
        except Exception as e:
            raise AtmosIQException(e, sys)

    def initiate_feature_engineering(self):
        try:
            feature_columns = []
            forecast_root = os.path.normpath(os.path.join(self.transformation_artifact.gold_dir, "..", "..", "data_ingestion", "forecasts"))
            for file_name in sorted(os.listdir(self.transformation_artifact.gold_dir)):
                if not file_name.endswith("_gold.parquet"):
                    continue
                location_id = file_name.replace("_gold.parquet", "")
                df = read_parquet(os.path.join(self.transformation_artifact.gold_dir, file_name))
                fpath = os.path.join(forecast_root, f"{location_id}_forecast.parquet")
                fc = read_parquet(fpath) if os.path.exists(fpath) else None
                df = build_features(df, fc)
                self.guard.assert_lag_columns_causal(df, "time")
                self.guard.assert_forecast_features_causal(df)
                feature_columns = [c for c in df.columns if c not in ("time", "location_id")]
                save_parquet(df, os.path.join(self.config.features_dir, f"{location_id}_features.parquet"))
            version_id = hash_config({"columns": feature_columns, "hash": self.transformation_artifact.config_hash})[:16]
            if self.session is not None:
                if self.session.get(FeatureVersion, f"feat_{version_id}") is None:
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
