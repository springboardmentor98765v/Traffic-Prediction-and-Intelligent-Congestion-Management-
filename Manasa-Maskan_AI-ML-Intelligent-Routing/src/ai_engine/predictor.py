import os
import joblib
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# Project root directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# Path to trained model
MODEL_PATH = os.path.join(BASE_DIR, "src", "traffic_model.pkl")

# Load model
model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")


def predict_traffic(road_id, hour, day_of_week, month):
    """
    Predict vehicle count for a given road and time.
    """

    input_data = np.array(
        [[road_id, hour, day_of_week, month]],
        dtype=float
    )

    prediction = model.predict(input_data)

    return round(float(prediction[0]), 2)


# Test prediction
if __name__ == "__main__":
    result = predict_traffic(2, 18, 3, 11)
    print("Predicted Vehicle Count:", result)

def get_traffic_condition(vehicle_count):
    if vehicle_count <= 15:
        return "Low Traffic"
    elif vehicle_count <= 30:
        return "Moderate Traffic"
    else:
        return "High Traffic"