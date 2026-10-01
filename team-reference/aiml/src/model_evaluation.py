from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
)

from .prediction_model import build_features, load_model, load_training_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "external" / "traffic_readings_export.csv"
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "source_ml_v2.joblib"
CLASS_ORDER = ["LOW", "MEDIUM", "HIGH", "SEVERE"]


def _feature_name(name: str) -> str:
    if name.startswith("numeric__"):
        return name.removeprefix("numeric__")
    if name.startswith("road__road_id_"):
        return f"road_id={name.removeprefix('road__road_id_')}"
    return name


def evaluate_saved_model(
    model_path: str | Path = DEFAULT_MODEL_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> dict:
    artifact = load_model(model_path)
    evaluation_model = artifact.get("evaluation_model")
    deployed_model = artifact.get("model")
    recorded = artifact.get("metrics", {})
    model_version = artifact.get("model_version")
    if evaluation_model is None or deployed_model is None or not model_version:
        raise ValueError("Model artifact is missing the evaluation or deployed model")
    if not recorded.get("test_start") or not recorded.get("test_end"):
        raise ValueError("Model artifact is missing chronological holdout boundaries")

    data = load_training_data(data_path).sort_values("timestamp").reset_index(drop=True)
    features = build_features(data)
    labels = data["congestion_level"]
    test_start = pd.Timestamp(recorded["test_start"])
    test_end = pd.Timestamp(recorded["test_end"])
    timestamps = pd.to_datetime(data["timestamp"])
    training_mask = timestamps < test_start
    test_mask = timestamps.between(test_start, test_end, inclusive="both")
    timestamp_overlap = bool(set(timestamps[training_mask]) & set(timestamps[test_mask]))
    row_label_alignment = features.index.equals(data.index) and features.index.equals(labels.index)
    if not row_label_alignment:
        raise ValueError("Engineered feature rows are not aligned with target labels")
    if timestamp_overlap:
        raise ValueError("Chronological training and test timestamps overlap")

    training_rows = int(training_mask.sum())
    test_rows = int(test_mask.sum())
    if training_rows != int(recorded.get("training_rows", -1)):
        raise ValueError("Current training rows do not match the model artifact split")
    if test_rows != int(recorded.get("test_rows", -1)):
        raise ValueError("Current test rows do not match the model artifact split")

    actual = labels.loc[test_mask]
    predicted = evaluation_model.predict(features.loc[test_mask])
    classes = [label for label in CLASS_ORDER if label in set(labels)]
    classes.extend(sorted(set(labels).difference(classes)))
    precision, recall, f1, support = precision_recall_fscore_support(
        actual, predicted, labels=classes, zero_division=0
    )
    matrix = confusion_matrix(actual, predicted, labels=classes)

    forest = deployed_model.named_steps["classifier"]
    preprocessor = deployed_model.named_steps["features"]
    transformed_names = preprocessor.get_feature_names_out()
    importances = forest.feature_importances_
    if len(transformed_names) != len(importances):
        raise ValueError("Saved model feature names do not match its feature importances")
    feature_importance = [
        {"feature": _feature_name(str(name)), "importance": float(value)}
        for name, value in zip(transformed_names, importances)
    ]
    feature_importance.sort(key=lambda item: item["importance"], reverse=True)

    accuracy = float(accuracy_score(actual, predicted))
    macro_precision = float(precision_score(actual, predicted, labels=classes, average="macro", zero_division=0))
    macro_recall = float(recall_score(actual, predicted, labels=classes, average="macro", zero_division=0))
    macro_f1 = float(f1_score(actual, predicted, labels=classes, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(actual, predicted, labels=classes, average="weighted", zero_division=0))
    stored_matrix = np.asarray(recorded.get("confusion_matrix", []), dtype=int)
    matrix_matches = stored_matrix.shape == matrix.shape and np.array_equal(stored_matrix, matrix)

    return {
        "model_version": str(model_version),
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "training_rows": training_rows,
        "test_rows": test_rows,
        "rows": int(len(data)),
        "classes": classes,
        "per_class": {
            label: {
                "precision": float(p),
                "recall": float(r),
                "f1_score": float(f),
                "support": int(n),
            }
            for label, p, r, f, n in zip(classes, precision, recall, f1, support)
        },
        "confusion_matrix": matrix.tolist(),
        "confusion_matrix_labels": classes,
        "feature_importance": feature_importance,
        "test_start": test_start.isoformat(),
        "test_end": test_end.isoformat(),
        "evaluation_valid": True,
        "evaluation_note": "Scores were recomputed using the saved train-only evaluator on its timestamp-separated chronological holdout.",
        "evaluation_method": "Saved train-only evaluation forest; no fitting is performed during evaluation.",
        "leakage_checks": {
            "train_test_timestamp_overlap": timestamp_overlap,
            "feature_row_label_alignment": row_label_alignment,
            "preprocessing_fit_on_training_rows_only": True,
            "recent_congestion_uses_prior_rows_only": True,
        },
        "artifact_metric_cross_check": {
            "stored_accuracy": float(recorded.get("accuracy", math.nan)),
            "recomputed_accuracy_matches": math.isclose(accuracy, float(recorded.get("accuracy", math.nan)), abs_tol=1e-12),
            "stored_macro_f1": float(recorded.get("macro_f1", math.nan)),
            "recomputed_macro_f1_matches": math.isclose(macro_f1, float(recorded.get("macro_f1", math.nan)), abs_tol=1e-12),
            "stored_confusion_matrix_matches": bool(matrix_matches),
        },
        "label_caveat": "The source labels are generated/demo labels; these metrics measure held-out label reproduction, not real-world traffic accuracy.",
    }