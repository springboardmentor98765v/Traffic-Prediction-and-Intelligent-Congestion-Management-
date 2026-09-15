import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error


# Load Sharmila's historical traffic data
DATA_PATH = (
    "Sharmila_Data-Engineering-Traffic-Monitoring/"
    "TrafficVision/data/traffic.csv"
)

df = pd.read_csv(DATA_PATH)

# Convert DateTime
df["DateTime"] = pd.to_datetime(df["DateTime"])

# Feature engineering
df["hour"] = df["DateTime"].dt.hour
df["day_of_week"] = df["DateTime"].dt.dayofweek
df["month"] = df["DateTime"].dt.month

# Features and target
X = df[
    [
        "Junction",
        "hour",
        "day_of_week",
        "month",
    ]
]

y = df["Vehicles"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

# Train model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

# Predictions
predictions = model.predict(X_test)

# Evaluation
mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(
    y_test,
    predictions,
) ** 0.5

print("M2 Traffic Prediction Model")
print("----------------------------")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# Save model
MODEL_PATH = "Manasa-Maskan_AI-ML-Intelligent-Routing/src/m2_traffic_model.pkl"

joblib.dump(model, MODEL_PATH)

print()
print("Model saved successfully!")
print(MODEL_PATH)