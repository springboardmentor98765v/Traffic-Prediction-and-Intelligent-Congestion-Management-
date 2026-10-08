from pathlib import Path
import joblib
import pandas as pd


class RecommendationEngine:
    """
    Generates simple, explainable traffic recommendations using:

    1. M2 trained congestion model
    2. Historical traffic trends from Intern 2
    3. Historical baseline data
    """

    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        self.model_path = (
            project_root / "ai-engine" / "models" / "model-v1.joblib"
        )

        self.traffic_path = (
            project_root
            / "ai-engine"
            / "data"
            / "historical_traffic_4weeks_cleaned.csv"
        )

        self.baseline_path = (
            project_root
            / "ai-engine"
            / "data"
            / "historical_baseline.csv"
        )

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained model not found: {self.model_path}"
            )

        if not self.traffic_path.exists():
            raise FileNotFoundError(
                f"Historical traffic data not found: {self.traffic_path}"
            )

        self.model = joblib.load(self.model_path)

        self.traffic = pd.read_csv(self.traffic_path)
        self.baseline = pd.read_csv(self.baseline_path)

        self.traffic["timestamp"] = pd.to_datetime(
            self.traffic["timestamp"]
        )

    def _predict_latest(self, road_id: str):
        """Use the M2 model on the latest historical observation."""

        road_data = self.traffic[
            self.traffic["road_id"] == road_id
        ].sort_values("timestamp")

        if road_data.empty:
            return None

        row = road_data.iloc[-1]

        timestamp = row["timestamp"]

        input_data = pd.DataFrame(
            [
                {
                    "vehicle_count": float(row["vehicle_count"]),
                    "avg_speed_kmph": float(row["avg_speed_kmph"]),
                    "road_capacity": float(row["road_capacity"]),
                    "road_length_km": float(row["road_length_km"]),
                    "traffic_density_vehicles_per_km": float(
                        row["traffic_density_vehicles_per_km"]
                    ),
                    "hour": int(timestamp.hour),
                    "day_of_week": int(timestamp.dayofweek),
                    "is_weekend": int(timestamp.dayofweek >= 5),
                    "road_id": road_id,
                }
            ]
        )

        prediction = str(self.model.predict(input_data)[0])

        probabilities = self.model.predict_proba(input_data)[0]
        confidence = float(probabilities.max())

        return {
            "level": prediction,
            "confidence": confidence,
            "timestamp": timestamp,
        }

    def _find_peak_hours(self, road_id: str):
        """Find recurring high-traffic hours from historical data."""

        road_data = self.traffic[
            self.traffic["road_id"] == road_id
        ].copy()

        if road_data.empty:
            return []

        road_data["hour"] = road_data["timestamp"].dt.hour

        hourly = (
            road_data.groupby("hour")
            .agg(
                avg_density=(
                    "traffic_density_vehicles_per_km",
                    "mean",
                ),
                avg_speed=("avg_speed_kmph", "mean"),
                avg_vehicle_count=("vehicle_count", "mean"),
            )
            .reset_index()
        )

        # Rank hours using density and vehicle volume.
        hourly["traffic_score"] = (
            hourly["avg_density"].rank(pct=True)
            + hourly["avg_vehicle_count"].rank(pct=True)
            + (1 - hourly["avg_speed"].rank(pct=True))
        )

        peak_hours = hourly.sort_values(
            "traffic_score",
            ascending=False,
        ).head(3)

        return peak_hours["hour"].astype(int).tolist()

    def generate(self, road_id: str):
        """Generate explainable recommendations for one road."""

        latest = self._predict_latest(road_id)

        if latest is None:
            return []

        peak_hours = self._find_peak_hours(road_id)

        recommendations = []

        predicted_level = latest["level"]
        confidence = latest["confidence"]
        current_hour = latest["timestamp"].hour

        # --------------------------------------------------------
        # Recommendation 1: predicted congestion
        # --------------------------------------------------------

        if predicted_level in {"High", "Severe"}:
            recommendations.append(
                {
                    "recommendation_text": (
                        "Consider leaving 15 minutes earlier "
                        "to avoid predicted congestion."
                    ),
                    "based_on": (
                        f"M2 model predicts {predicted_level} congestion "
                        f"with {confidence:.0%} confidence."
                    ),
                }
            )

        elif predicted_level == "Medium":
            recommendations.append(
                {
                    "recommendation_text": (
                        "Allow additional travel time because "
                        "moderate congestion is predicted."
                    ),
                    "based_on": (
                        f"M2 model predicts Medium congestion "
                        f"with {confidence:.0%} confidence."
                    ),
                }
            )

        # --------------------------------------------------------
        # Recommendation 2: historical recurring peak
        # --------------------------------------------------------

        if peak_hours:
            sorted_hours = sorted(peak_hours)

            # Convert consecutive peak hours into readable time windows.
            windows = []
            start = sorted_hours[0]
            end = sorted_hours[0]

            for hour in sorted_hours[1:]:
                if hour == end + 1:
                    end = hour
                else:
                    windows.append((start, end))
                    start = hour
                    end = hour

            windows.append((start, end))

            formatted_windows = []

            for start, end in windows:
                if start == end:
                    formatted_windows.append(f"{start:02d}:00")
                else:
                    formatted_windows.append(
                        f"{start:02d}:00–{end:02d}:00"
                    )

            formatted_peak_periods = ", ".join(formatted_windows)

            recommendations.append(
                {
                    "recommendation_text": (
                        f"Avoid the recurring busy period "
                        f"({formatted_peak_periods}) when possible."
                    ),
                    "based_on": (
                        "Historical traffic trends for this road "
                        "show consistently higher traffic during "
                        "these periods."
                    ),
                }
            )

        # --------------------------------------------------------
        # Recommendation 3: current hour is historically busy
        # --------------------------------------------------------

        if current_hour in peak_hours:
            recommendations.append(
                {
                    "recommendation_text": (
                        "Traffic is currently within a historically "
                        "busy period, so consider delaying the trip "
                        "or using an alternate route."
                    ),
                    "based_on": (
                        f"Historical trend identifies {current_hour:02d}:00 "
                        "as a recurring high-traffic period."
                    ),
                }
            )

        # Keep the API response concise.
        return recommendations[:3]
