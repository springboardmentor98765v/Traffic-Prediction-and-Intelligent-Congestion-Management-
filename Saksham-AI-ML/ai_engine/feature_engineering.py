"""
Feature engineering module for TrafficVision AI Engine (Milestone 2).
Transforms raw traffic time-series records into model-ready features.
"""
from datetime import datetime
import numpy as np
import pandas as pd


def extract_time_features(dt: datetime) -> dict:
    """Extracts temporal features from a timestamp."""
    hour = dt.hour
    day_of_week = dt.weekday()  # Monday=0, Sunday=6
    is_weekend = 1 if day_of_week in [5, 6] else 0
    # Peak windows: Morning (08:00 - 11:00), Evening (17:00 - 20:00)
    is_rush_hour = 1 if (8 <= hour <= 11) or (17 <= hour <= 20) else 0

    return {
        "hour_of_day": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "is_rush_hour": is_rush_hour,
    }


def prepare_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepares and validates tabular features from input traffic records."""
    required_cols = ["road_id", "timestamp", "density", "vehicle_count"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Temporal feature derivations
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.weekday
    df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x in [5, 6] else 0)
    df["is_rush_hour"] = df["hour_of_day"].apply(
        lambda h: 1 if (8 <= h <= 11) or (17 <= h <= 20) else 0
    )

    # Rolling window aggregations per road segment
    df = df.sort_values(by=["road_id", "timestamp"]).reset_index(drop=True)
    df["rolling_avg_density"] = (
        df.groupby("road_id")["density"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )
    df["rolling_avg_vehicle_count"] = (
        df.groupby("road_id")["vehicle_count"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    return df