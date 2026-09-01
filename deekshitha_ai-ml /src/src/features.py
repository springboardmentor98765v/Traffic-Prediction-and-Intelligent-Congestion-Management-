"""Feature engineering utilities for traffic data."""

from __future__ import annotations

import pandas as pd


def add_time_features(data: pd.DataFrame, timestamp_column: str) -> pd.DataFrame:
    """Add calendar features derived from a timestamp column."""
    result = data.copy()
    timestamp = pd.to_datetime(result[timestamp_column])
    result["hour"] = timestamp.dt.hour
    result["day_of_week"] = timestamp.dt.dayofweek
    result["is_weekend"] = timestamp.dt.dayofweek >= 5
    return result
