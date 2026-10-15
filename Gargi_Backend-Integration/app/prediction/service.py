import os

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.database.models import TrafficRecord


MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "ml",
    "models",
    "congestion_model.joblib",
)


class PredictionService:
    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is not None:
            return

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Train the model first."
            )

        self.model = joblib.load(MODEL_PATH)

    def predict_congestion(
        self,
        db: Session,
        road_id: int,
        prediction_time,
    ):
        self.load_model()

        latest_record = (
            db.query(TrafficRecord)
            .filter(TrafficRecord.road_id == road_id)
            .order_by(TrafficRecord.recorded_at.desc())
            .first()
        )

        if not latest_record:
            raise ValueError(f"No traffic data found for road {road_id}")

        prediction_time = pd.to_datetime(prediction_time)

        features = pd.DataFrame(
            [
                {
                    "road_id": road_id,
                    "hour": prediction_time.hour,
                    "day_of_week": prediction_time.dayofweek,
                    "vehicle_count": latest_record.vehicle_count,
                    "density": latest_record.density,
                }
            ]
        )

        prediction = self.model.predict(features)[0]

        confidence = None

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(features)[0]
            confidence = float(max(probabilities))

        return {
            "road_id": road_id,
            "predicted_level": prediction,
            "confidence": (
                round(confidence, 2) if confidence is not None else None
            ),
            "model_version": "random-forest-v1",
        }

    def get_peak_hours(
        self,
        db: Session,
        road_id: int,
    ):
        records = (
            db.query(TrafficRecord)
            .filter(TrafficRecord.road_id == road_id)
            .all()
        )

        if not records:
            raise ValueError(f"No traffic data found for road {road_id}")

        hourly_density = {}

        for record in records:
            hour = record.recorded_at.hour

            if hour not in hourly_density:
                hourly_density[hour] = []

            hourly_density[hour].append(record.density)

        hourly_average = {
            hour: sum(values) / len(values)
            for hour, values in hourly_density.items()
        }

        sorted_hourly_densities = sorted(hourly_average.values())
        percentile_index = int(0.75 * (len(sorted_hourly_densities) - 1))
        relative_peak_threshold = sorted_hourly_densities[percentile_index]
        absolute_peak_threshold = 0.65
        peak_threshold = (
            absolute_peak_threshold
            if sorted_hourly_densities[-1] >= absolute_peak_threshold
            else relative_peak_threshold
        )

        peak_hours = [
            hour
            for hour, density in hourly_average.items()
            if density >= peak_threshold
        ]

        peak_hours.sort()

        windows = []

        if peak_hours:
            start_hour = peak_hours[0]
            previous_hour = peak_hours[0]

            for hour in peak_hours[1:]:
                if hour == previous_hour + 1:
                    previous_hour = hour
                else:
                    windows.append(
                        {
                            "start": f"{start_hour:02d}:00",
                            "end": f"{previous_hour + 1:02d}:00",
                        }
                    )

                    start_hour = hour
                    previous_hour = hour

            windows.append(
                {
                    "start": f"{start_hour:02d}:00",
                    "end": f"{previous_hour + 1:02d}:00",
                }
            )

        return {
            "road_id": road_id,
            "peak_windows": windows,
        }

    def estimate_delay(
        self,
        db: Session,
        road_id: int,
    ):
        latest_record = (
            db.query(TrafficRecord)
            .filter(TrafficRecord.road_id == road_id)
            .order_by(TrafficRecord.recorded_at.desc())
            .first()
        )

        if not latest_record:
            raise ValueError(f"No traffic data found for road {road_id}")

        density = latest_record.density
        base_travel_time = 10.0

        if density <= 0.3:
            delay = 0.0
        elif density <= 0.5:
            delay = base_travel_time * 0.10
        elif density <= 0.65:
            delay = base_travel_time * 0.25
        elif density <= 0.85:
            delay = base_travel_time * 0.50
        else:
            delay = base_travel_time * 0.80

        confidence = min(
            0.95,
            0.60 + density * 0.35,
        )

        return {
            "road_id": road_id,
            "estimated_delay_minutes": round(
                delay,
                2,
            ),
            "confidence": round(
                confidence,
                2,
            ),
        }


prediction_service = PredictionService()