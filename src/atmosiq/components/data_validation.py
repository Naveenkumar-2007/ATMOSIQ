import os
import sys
import uuid

import pandas as pd

from atmosiq.db.models import ValidationRun
from atmosiq.db.repositories import RunRepository
from atmosiq.entity.artifact_entity import DataValidationArtifact
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import (
    read_parquet,
    read_yaml_file,
    save_parquet,
    write_json_file,
)

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
