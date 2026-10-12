from pathlib import Path

import joblib
import pandas as pd


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "Manasa-Maskan_AI-ML-Intelligent-Routing"
    / "src"
    / "m2_traffic_model.pkl"
)


class VehicleCountPredictionService:
    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is not None:
            return

        if not MODEL_PATH.is_file():
            raise FileNotFoundError(
                f"Manasa vehicle-count model not found: {MODEL_PATH}"
            )

        self.model = joblib.load(MODEL_PATH)

        expected_features = [
            "Junction",
            "hour",
            "day_of_week",
            "month",
        ]

        actual_features = list(
            getattr(self.model, "feature_names_in_", [])
        )

        if actual_features != expected_features:
            self.model = None
            raise ValueError(
                "Unexpected vehicle-count model features: "
                f"{actual_features}"
            )

    def predict(self, junction: int, prediction_time):
        self.load_model()

        prediction_time = pd.Timestamp(prediction_time)

        features = pd.DataFrame(
            [
                {
                    "Junction": junction,
                    "hour": prediction_time.hour,
                    "day_of_week": prediction_time.dayofweek,
                    "month": prediction_time.month,
                }
            ],
            columns=[
                "Junction",
                "hour",
                "day_of_week",
                "month",
            ],
        )

        vehicle_count = max(
            0.0,
            float(self.model.predict(features)[0]),
        )

        if vehicle_count < 10:
            condition = "Low Traffic"
        elif vehicle_count < 25:
            condition = "Medium Traffic"
        else:
            condition = "High Traffic"

        return {
            "junction": junction,
            "prediction_time": prediction_time.isoformat(),
            "predicted_vehicle_count": round(vehicle_count, 2),
            "traffic_condition": condition,
            "model_version": "manasa-random-forest-regressor-m2",
        }


vehicle_count_service = VehicleCountPredictionService()
