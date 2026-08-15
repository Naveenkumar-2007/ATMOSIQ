from datetime import UTC, datetime

import pandas as pd
import pytest

from atmosiq.utils.leakage_guard import LeakageGuard, LeakageViolation


def test_future_rows_detected():
    guard = LeakageGuard(issue_time=datetime(2025, 6, 1, 12, 0, tzinfo=UTC))
    df = pd.DataFrame({"time": pd.to_datetime(["2025-06-01 13:00"], utc=True)})
    with pytest.raises(LeakageViolation):
        guard.assert_no_future_rows(df, "time")


def test_lead_columns_detected():
    guard = LeakageGuard()
    df = pd.DataFrame({"lead_temperature": [1.0], "time": pd.to_datetime(["2025-06-01"], utc=True)})
    with pytest.raises(LeakageViolation):
        guard.assert_lag_columns_causal(df, "time")


def test_preprocessor_fit_beyond_train():
    guard = LeakageGuard()
    with pytest.raises(LeakageViolation):
        guard.assert_preprocessor_fit_bounds(
            datetime(2025, 7, 1, tzinfo=UTC), datetime(2025, 6, 1, tzinfo=UTC)
        )


def test_causal_data_passes():
    guard = LeakageGuard(issue_time=datetime(2025, 6, 1, 12, 0, tzinfo=UTC))
    df = pd.DataFrame({"time": pd.to_datetime(["2025-06-01 10:00", "2025-06-01 11:00"], utc=True)})
    guard.assert_no_future_rows(df, "time")
