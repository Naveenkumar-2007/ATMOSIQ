
import pandas as pd

from atmosiq.exception.exception import AtmosIQException


class LeakageViolation(AtmosIQException):
    """Raised when future information leaks into features/targets."""


class LeakageGuard:
    def __init__(self, issue_time=None):
        self.issue_time = issue_time

    def assert_no_future_rows(self, df, time_col, reference=None):
        reference = reference or self.issue_time
        if reference is None:
            return
        times = pd.to_datetime(df[time_col], utc=True)
        future = times[times > pd.Timestamp(reference)]
        if len(future) > 0:
            raise LeakageViolation(f"{len(future)} rows newer than issue_time leaked into features")

    def assert_lag_columns_causal(self, df, time_col):
        suspect = [c for c in df.columns if c.startswith(("lead_", "future_"))]
        if suspect:
            raise LeakageViolation(f"Non-causal columns present: {suspect}")

    def assert_preprocessor_fit_bounds(self, fit_max_time, train_end):
        if fit_max_time > train_end:
            raise LeakageViolation(f"Preprocessor fitted beyond train split end ({fit_max_time} > {train_end})")

    def assert_forecast_features_causal(self, df):
        if {"forecast_issue_time", "time"}.issubset(df.columns):
            bad = df[pd.to_datetime(df["forecast_issue_time"], utc=True) > pd.to_datetime(df["time"], utc=True)]
            if len(bad) > 0:
                raise LeakageViolation("Provider forecast features indexed by issue_time after observation time")

    def assert_target_alignment(self, df, horizon_hours, time_col="time"):
        target_col = f"target_{horizon_hours}h"
        if target_col not in df.columns:
            return
        valid = df.dropna(subset=[target_col])
        if len(valid) == 0:
            return
        last_row_time = pd.to_datetime(valid[time_col], utc=True).max()
        last_target_time = last_row_time + pd.Timedelta(hours=horizon_hours)
        data_end = pd.to_datetime(df[time_col], utc=True).max()
        if last_target_time > data_end + pd.Timedelta(minutes=1):
            raise LeakageViolation("Target references observations beyond available data")
