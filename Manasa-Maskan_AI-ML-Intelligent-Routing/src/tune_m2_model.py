from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR.parent
    / "Sharmila_Data-Engineering-Traffic-Monitoring"
    / "TrafficVision"
    / "data"
    / "traffic.csv"
)

MODEL_PATH = BASE_DIR / "src" / "m2_traffic_model_tuned.pkl"


# ---------------------------------------------------------
# Load traffic dataset
# ---------------------------------------------------------

df = pd.read_csv(DATA_PATH)

df["DateTime"] = pd.to_datetime(df["DateTime"])


# ---------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Split data
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)


# ---------------------------------------------------------
# Create validation set
# ---------------------------------------------------------

X_train_main, X_validation, y_train_main, y_validation = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
)


# ---------------------------------------------------------
# Models to compare
# ---------------------------------------------------------

models = {
    "Model 1 - Baseline": RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
    ),

    "Model 2 - More Trees": RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    ),

    "Model 3 - Controlled Depth": RandomForestRegressor(
        n_estimators=150,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
    ),

    "Model 4 - More Trees + Controlled Depth": RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    ),
}


# ---------------------------------------------------------
# Train and compare models
# ---------------------------------------------------------

results = []

print("M2 Random Forest Model Tuning")
print("=============================")
print()

for name, model in models.items():

    print(f"Training: {name}")

    model.fit(
        X_train_main,
        y_train_main,
    )

    validation_predictions = model.predict(X_validation)

    mae = mean_absolute_error(
        y_validation,
        validation_predictions,
    )

    rmse = mean_squared_error(
        y_validation,
        validation_predictions,
    ) ** 0.5

    results.append(
        {
            "name": name,
            "model": model,
            "mae": mae,
            "rmse": rmse,
        }
    )

    print(f"Validation MAE: {mae:.2f}")
    print(f"Validation RMSE: {rmse:.2f}")
    print()


# ---------------------------------------------------------
# Select best model
# ---------------------------------------------------------

best_result = min(
    results,
    key=lambda result: result["mae"],
)

best_model = best_result["model"]


print("--------------------------------")
print("Best Model:")
print(best_result["name"])
print(f"Best Validation MAE: {best_result['mae']:.2f}")
print(f"Best Validation RMSE: {best_result['rmse']:.2f}")


# ---------------------------------------------------------
# Final evaluation on test data
# ---------------------------------------------------------

test_predictions = best_model.predict(X_test)

test_mae = mean_absolute_error(
    y_test,
    test_predictions,
)

test_rmse = mean_squared_error(
    y_test,
    test_predictions,
) ** 0.5


print()
print("Final Test Evaluation")
print("---------------------")
print(f"Test MAE: {test_mae:.2f}")
print(f"Test RMSE: {test_rmse:.2f}")


# ---------------------------------------------------------
# Save tuned model
# ---------------------------------------------------------

joblib.dump(
    best_model,
    MODEL_PATH,
)

print()
print("Tuned model saved successfully!")
print(MODEL_PATH)