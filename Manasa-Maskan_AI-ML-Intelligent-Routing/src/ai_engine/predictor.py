import os
import joblib
import pandas as pd


# Get the path of the current folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# M2 trained model path
MODEL_PATH = os.path.join(
    BASE_DIR,
    "m2_traffic_model.pkl"
)

# Load the trained M2 model
model = joblib.load(MODEL_PATH)


def predict_traffic(
    junction: int,
    hour: int,
    day_of_week: int,
    month: int
):
    """
    Predict the number of vehicles using the M2 model.
    """

    data = pd.DataFrame(
        [
            {
                "Junction": junction,
                "hour": hour,
                "day_of_week": day_of_week,
                "month": month,
            }
        ]
    )

    prediction = model.predict(data)[0]

    return round(float(prediction), 2)


def get_traffic_condition(vehicle_count: float):
    """
    Convert predicted vehicle count into a traffic condition.
    """

    if vehicle_count < 10:
        return "Low Traffic"

    elif vehicle_count < 25:
        return "Medium Traffic"

    else:
        return "High Traffic"