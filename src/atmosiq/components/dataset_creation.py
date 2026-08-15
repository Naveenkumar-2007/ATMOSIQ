import os
import sys

import pandas as pd

from atmosiq.common.weather_codes import compass_index, condition_index
from atmosiq.components.task_registry import TASKS
from atmosiq.db.models import DatasetVersion
from atmosiq.entity.artifact_entity import DatasetCreationArtifact
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.leakage_guard import LeakageGuard
from atmosiq.utils.main_utils.utils import hash_config, read_parquet, save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.dataset_creation")


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
        import numpy as np
        threshold = self.config.app.raw["rain"]["occurrence_threshold_mm"]
        for task, (source, kind, horizons) in TASKS.items():
            if source not in df.columns:
                continue
            future_base = df[source]
            for horizon in horizons:
                future = future_base.shift(-horizon)
                if kind == "regression":
                    col = future
                elif kind == "binary":
                    col = pd.Series(np.where(future.isna(), np.nan, (future > threshold).astype(float)), index=df.index)
                elif kind == "condition_class":
                    col = future.map(condition_index)
                elif kind == "direction_class":
                    col = future.map(compass_index)
                else:
                    col = future
                df[f"target_{task}_{horizon}h"] = col
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
                "tasks": {t: {"source": s, "kind": k, "horizons": h} for t, (s, k, h) in TASKS.items()},
                "feature_columns": self.feature_artifact.feature_columns,
                "split_policy": "chronological",
            }
            version_id = hash_config(manifest)[:16]
            manifest["dataset_version_id"] = f"ds_{version_id}"
            write_json_file(self.config.manifest_file_path, manifest)
            if self.session is not None:
                if self.session.get(DatasetVersion, f"ds_{version_id}") is None:
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
