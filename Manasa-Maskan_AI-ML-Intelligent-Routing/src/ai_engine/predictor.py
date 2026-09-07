import joblib
import pandas as pd
from pathlib import Path


MODEL_PATH = Path(__file__).resolve().parent.parent / "traffic_model.pkl"

model = joblib.load(MODEL_PATH)


def predict_traffic(
    road_id: int,
    hour: int,
    day_of_week: int,
    month: int,
):
    input_data = pd.DataFrame(
        {
            "road_id": [road_id],
            "hour": [hour],
            "day_of_week": [day_of_week],
            "month": [month],
        }
    )

    prediction = model.predict(input_data)[0]

    return prediction