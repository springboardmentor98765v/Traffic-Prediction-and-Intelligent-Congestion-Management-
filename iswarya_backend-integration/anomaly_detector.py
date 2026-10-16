from pathlib import Path

import numpy as np
import pandas as pd

# Look for CSV files directly in the current folder where this script resides
CURRENT_DIR = Path(__file__).resolve().parent

TRAFFIC_DATA = CURRENT_DIR / "historical_traffic_4weeks_cleaned.csv"
BASELINE_DATA = CURRENT_DIR / "historical_baseline.csv"


class AnomalyDetector:
    """
    Historical-baseline anomaly detector for TrafficVision AI.

    The detector compares an observation against expected traffic
    behavior for the same road, hour, and day of week.
    """

    def __init__(
        self,
        traffic_path: Path = TRAFFIC_DATA,
        baseline_path: Path = BASELINE_DATA,
    ):
        self.traffic_path = traffic_path
        self.baseline_path = baseline_path

        # Load the baseline data into self.baseline so merge works correctly
        self.baseline = pd.read_csv(self.baseline_path)

        self._prepare_historical_statistics()

    def _prepare_historical_statistics(self):
        """Calculate data-driven thresholds from historical traffic."""

        traffic = pd.read_csv(self.traffic_path)

        traffic["timestamp"] = pd.to_datetime(traffic["timestamp"])
        traffic["hour"] = traffic["timestamp"].dt.hour
        traffic["day_of_week"] = traffic["timestamp"].dt.dayofweek

        df = traffic.merge(
            self.baseline,
            on=["road_id", "hour", "day_of_week"],
            how="left",
        )

        # Individual historical deviations
        vehicle_deviation = (
            (
                df["vehicle_count"]
                - df["expected_vehicle_count"]
            ).abs()
            / df["expected_vehicle_count"].replace(0, np.nan)
        )

        speed_deviation = (
            (
                df["expected_speed_kmph"]
                - df["avg_speed_kmph"]
            )
            / df["expected_speed_kmph"].replace(0, np.nan)
        ).clip(lower=0)

        density_deviation = (
            (
                df["traffic_density_vehicles_per_km"]
                - df["expected_density"]
            )
            / df["expected_density"].replace(0, np.nan)
        ).clip(lower=0)

        combined_deviation = (
            0.40 * vehicle_deviation
            + 0.30 * speed_deviation
            + 0.30 * density_deviation
        )

        self.anomaly_threshold = combined_deviation.quantile(0.95)
        self.incident_threshold = combined_deviation.quantile(0.99)

        self.strong_vehicle_threshold = vehicle_deviation.quantile(0.95)
        self.strong_speed_threshold = speed_deviation.quantile(0.95)
        self.strong_density_threshold = density_deviation.quantile(0.95)

    def _get_baseline(self, road_id, hour, day_of_week):
        """Return the historical baseline for a road/time combination."""

        matches = self.baseline[
            (self.baseline["road_id"] == road_id)
            & (self.baseline["hour"] == hour)
            & (self.baseline["day_of_week"] == day_of_week)
        ]

        if matches.empty:
            return None

        return matches.iloc[0]

    def analyze(
        self,
        road_id,
        timestamp,
        vehicle_count,
        avg_speed_kmph,
        traffic_density,
    ):
        """
        Analyze a single traffic observation.

        Returns a dictionary containing expected values,
        deviations, anomaly score, and classification.
        """

        timestamp = pd.Timestamp(timestamp)

        hour = timestamp.hour
        day_of_week = timestamp.dayofweek

        baseline = self._get_baseline(
            road_id,
            hour,
            day_of_week,
        )

        if baseline is None:
            return {
                "road_id": road_id,
                "time": timestamp.isoformat(),
                "anomaly_class": "unknown",
                "reason": "No historical baseline available",
            }

        expected_vehicle = float(
            baseline["expected_vehicle_count"]
        )

        expected_speed = float(
            baseline["expected_speed_kmph"]
        )

        expected_density = float(
            baseline["expected_density"]
        )

        # Calculate deviations
        vehicle_deviation = abs(
            vehicle_count - expected_vehicle
        ) / max(expected_vehicle, 1e-9)

        speed_deviation = max(
            0,
            expected_speed - avg_speed_kmph,
        ) / max(expected_speed, 1e-9)

        density_deviation = max(
            0,
            traffic_density - expected_density,
        ) / max(expected_density, 1e-9)

        # Combined weighted anomaly score
        anomaly_score = (
            0.40 * vehicle_deviation
            + 0.30 * speed_deviation
            + 0.30 * density_deviation
        )

        # Count independently strong signals
        strong_signal_count = sum(
            [
                vehicle_deviation >= self.strong_vehicle_threshold,
                speed_deviation >= self.strong_speed_threshold,
                density_deviation >= self.strong_density_threshold,
            ]
        )

        # Classification
        if (
            anomaly_score >= self.incident_threshold
            and strong_signal_count >= 2
        ):
            anomaly_class = "possible_incident"

        elif anomaly_score >= self.anomaly_threshold:
            anomaly_class = "traffic_anomaly"

        else:
            anomaly_class = "normal"

        return {
            "road_id": road_id,
            "time": timestamp.isoformat(),
            "expected_level": baseline["expected_congestion"],
            "vehicle_count": vehicle_count,
            "expected_vehicle_count": round(expected_vehicle, 2),
            "avg_speed_kmph": avg_speed_kmph,
            "expected_speed_kmph": round(expected_speed, 2),
            "traffic_density": traffic_density,
            "expected_density": round(expected_density, 2),
            "vehicle_deviation": round(vehicle_deviation, 4),
            "speed_deviation": round(speed_deviation, 4),
            "density_deviation": round(density_deviation, 4),
            "anomaly_score": round(anomaly_score, 4),
            "strong_signal_count": strong_signal_count,
            "anomaly_class": anomaly_class,
        }