from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


# Get project paths
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR.parent
    / "Sharmila_Data-Engineering-Traffic-Monitoring"
    / "TrafficVision"
    / "data"
    / "traffic.csv"
)

MODEL_PATH = BASE_DIR / "src" / "m2_traffic_model.pkl"


# Load dataset
df = pd.read_csv(DATA_PATH)

# Convert DateTime
df["DateTime"] = pd.to_datetime(df["DateTime"])


# Feature engineering
df["hour"] = df["DateTime"].dt.hour
df["day_of_week"] = df["DateTime"].dt.dayofweek
df["month"] = df["DateTime"].dt.month


# Features
X = df[
    [
        "Junction",
        "hour",
        "day_of_week",
        "month",
    ]
]

# Target
y = df["Vehicles"]


# Create the same train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)


# Load trained M2 model
model = joblib.load(MODEL_PATH)


# Make predictions
predictions = model.predict(X_test)


# Calculate evaluation metrics
mae = mean_absolute_error(y_test, predictions)

rmse = mean_squared_error(
    y_test,
    predictions,
) ** 0.5


# Display results
print("M2 Model Evaluation")
print("--------------------")
print(f"Test samples: {len(X_test)}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

print()
print("Evaluation completed successfully.")