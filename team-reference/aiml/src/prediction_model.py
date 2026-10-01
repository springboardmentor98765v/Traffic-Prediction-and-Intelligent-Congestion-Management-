from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

MODEL_VERSION = "ml-v2"
ROAD_CAPACITY = 200.0
FEATURE_COLUMNS = [
    "road_id", "vehicle_count", "average_speed", "density", "hour",
    "day_of_week", "is_peak_hour", "recent_congestion",
]
NUMERIC_FEATURES = [column for column in FEATURE_COLUMNS if column != "road_id"]
CATEGORICAL_FEATURES = ["road_id"]


def normalize_road_id(value) -> str:
    road_id = str(value).strip().upper()
    if not road_id:
        raise ValueError("road_id is required")
    if road_id.startswith("R"):
        return road_id
    if road_id.isdigit():
        return f"R{int(road_id):03d}"
    return road_id.replace(" ", "-")


def load_training_data(data_path: str | Path) -> pd.DataFrame:
    """Load the Data Engineering export into the model's canonical schema."""
    data = pd.read_csv(data_path).rename(columns={
        "recorded_at": "timestamp",
        "avg_speed_kmph": "average_speed",
    })
    required = {"road_id", "timestamp", "vehicle_count", "average_speed", "congestion_level"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Training data is missing fields: {sorted(missing)}")
    data["road_id"] = data["road_id"].map(normalize_road_id)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data["vehicle_count"] = pd.to_numeric(data["vehicle_count"], errors="raise")
    data["average_speed"] = pd.to_numeric(data["average_speed"], errors="raise")
    data["congestion_level"] = (
        data["congestion_level"].astype(str).str.upper().replace({"MODERATE": "MEDIUM"})
    )
    return data


def build_features(observations: pd.DataFrame, road_capacity: float = ROAD_CAPACITY) -> pd.DataFrame:
    """Create the features shared by training and inference."""
    frame = observations.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values(["road_id", "timestamp"])
    if "density" not in frame or frame["density"].isna().all():
        frame["density"] = frame["vehicle_count"] / road_capacity
    else:
        frame["density"] = pd.to_numeric(frame["density"], errors="raise")
    frame["hour"] = frame["timestamp"].dt.hour
    frame["day_of_week"] = frame["timestamp"].dt.dayofweek
    frame["is_peak_hour"] = frame["hour"].between(8, 10) | frame["hour"].between(17, 19)
    if "recent_congestion" not in frame or frame["recent_congestion"].isna().all():
        speed_signal = (frame["average_speed"] < 35).astype(float)
        frame["recent_congestion"] = (
            speed_signal.groupby(frame["road_id"])
            .transform(lambda values: values.shift(1).rolling(3, min_periods=1).mean())
            .fillna(speed_signal)
        )
    else:
        frame["recent_congestion"] = frame["recent_congestion"].fillna(0.0)
    return frame[FEATURE_COLUMNS].sort_index()


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            ("road", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=200,
        max_features="sqrt",
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=42,
    )
    return Pipeline(
        steps=[
            ("features", preprocessor),
            ("classifier", classifier),
        ]
    )


def train_model(data_path: str | Path, model_path: str | Path) -> dict:
    data = load_training_data(data_path)
    data = data.sort_values("timestamp").reset_index(drop=True)
    if data["congestion_level"].nunique() < 2:
        raise ValueError("Training data must contain at least two congestion classes")
    features = build_features(data)
    labels = data["congestion_level"]
    timestamps = data["timestamp"].drop_duplicates().sort_values().to_numpy()
    split_index = min(max(1, int(len(timestamps) * 0.8)), len(timestamps) - 1)
    split_timestamp = timestamps[split_index]
    training_mask = data["timestamp"] < split_timestamp
    training_features = features.loc[training_mask]
    test_features = features.loc[~training_mask]
    training_labels = labels.loc[training_mask]
    test_labels = labels.loc[~training_mask]
    evaluation_pipeline = build_pipeline()
    evaluation_pipeline.fit(training_features, training_labels)
    holdout_predictions = evaluation_pipeline.predict(test_features)
    metrics = {
        "training_rows": int(len(training_labels)),
        "test_rows": int(len(test_labels)),
        "rows": int(len(data)),
        "chronological_holdout_rows": int(len(test_labels)),
        "test_start": pd.Timestamp(split_timestamp).isoformat(),
        "test_end": pd.Timestamp(data["timestamp"].max()).isoformat(),
        "evaluation_valid": True,
        "evaluation_note": "Chronological holdout split by timestamp; test timestamps were excluded from fitting.",
        "accuracy": float(accuracy_score(test_labels, holdout_predictions)),
        "macro_f1": float(f1_score(test_labels, holdout_predictions, average="macro", zero_division=0)),
        "classes": sorted(labels.unique().tolist()),
        "per_class": classification_report(
            test_labels, holdout_predictions, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            test_labels, holdout_predictions, labels=sorted(labels.unique().tolist())
        ).tolist(),
    }
    model = build_pipeline()
    model.fit(features, labels)
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": model,
        "evaluation_model": evaluation_pipeline,
        "model_version": MODEL_VERSION,
        "metrics": metrics,
    }, model_path, compress=3)
    return metrics


def load_model(model_path: str | Path) -> dict:
    return joblib.load(model_path)


def predict_observation(artifact: dict, road_id: str, vehicle_count: float,
                        average_speed: float, timestamp: pd.Timestamp,
                        recent_congestion: float | None = None,
                        density: float | None = None) -> dict:
    observation = pd.DataFrame([{
        "road_id": normalize_road_id(road_id), "vehicle_count": vehicle_count,
        "average_speed": average_speed, "timestamp": timestamp,
        "recent_congestion": recent_congestion,
        "density": density,
    }])
    features = build_features(observation)
    prediction = artifact["model"].predict(features)[0]
    probabilities = artifact["model"].predict_proba(features)[0]
    return {
        "predicted_level": str(prediction),
        "confidence": float(np.max(probabilities)),
        "model_version": artifact["model_version"],
    }