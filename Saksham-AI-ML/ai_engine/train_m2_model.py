"""
Model training pipeline for TrafficVision AI Engine (Milestone 2).
Trains:
1. Congestion Level Classifier (Random Forest)
2. Delay Estimation Regressor (Random Forest)
Saves composite artifact to ai_engine/traffic_model_v2.joblib
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error, root_mean_squared_error

from ai_engine.feature_engineering import prepare_features_df

# Paths
DATA_PATH = "Data/traffic_dataset_1000_combined.csv"
MODEL_OUTPUT_PATH = "ai_engine/traffic_model_v2.joblib"

FEATURE_COLS = [
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "is_rush_hour",
    "density",
    "vehicle_count",
    "rolling_avg_density",
    "rolling_avg_vehicle_count",
]


def train():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    print(f"Loading dataset from {DATA_PATH}...")
    raw_df = pd.read_csv(DATA_PATH)

    print("Running feature engineering pipeline...")
    df = prepare_features_df(raw_df)

    # Clean target: standardize congestion levels
    df["congestion_level"] = df["congestion_level"].astype(str).str.upper().str.strip()
    valid_levels = {"LOW", "MEDIUM", "HIGH", "SEVERE"}
    df = df[df["congestion_level"].isin(valid_levels)].copy()

    # Synthetic delay derivation (if delay minutes not explicitly recorded in raw readings)
    # Delay directly scales with density, rush hour penalty, and vehicle count
    delay_baseline = df["density"] * 25.0
    rush_penalty = df["is_rush_hour"] * 8.0
    noise = np.random.normal(0, 1.5, size=len(df))
    df["delay_minutes"] = np.clip(delay_baseline + rush_penalty + noise, a_min=0.0, a_max=90.0)

    X = df[FEATURE_COLS]
    y_class = df["congestion_level"]
    y_reg = df["delay_minutes"]

    # Train/Test Split
    X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
        X, y_class, y_reg, test_size=0.2, random_state=42
    )

    print(f"Training Congestion Classifier on {len(X_train)} samples...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X_train, y_class_train)

    y_class_pred = clf.predict(X_test)
    print("\n--- Congestion Classification Report ---")
    print(classification_report(y_class_test, y_class_pred))

    print(f"Training Delay Regressor on {len(X_train)} samples...")
    reg = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    reg.fit(X_train, y_reg_train)

    y_reg_pred = reg.predict(X_test)
    mae = mean_absolute_error(y_reg_test, y_reg_pred)
    rmse = root_mean_squared_error(y_reg_test, y_reg_pred)
    print("--- Delay Regression Metrics ---")
    print(f"MAE: {mae:.2f} minutes | RMSE: {rmse:.2f} minutes")

    # Serialize composite bundle
    artifact = {
        "classifier": clf,
        "regressor": reg,
        "feature_cols": FEATURE_COLS,
        "model_version": "model-v1",
        "valid_classes": list(clf.classes_),
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
        },
    }

    joblib.dump(artifact, MODEL_OUTPUT_PATH)
    print(f"\nModel artifact successfully saved to {MODEL_OUTPUT_PATH}!")


if __name__ == "__main__":
    train()