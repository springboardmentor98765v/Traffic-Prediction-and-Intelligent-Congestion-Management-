import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sqlalchemy.orm import Session

from app.database.models import Road, TrafficRecord
from app.prediction.service import MODEL_PATH, prediction_service


def evaluate_model(db: Session, road_id: int):
    records = (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id == road_id)
        .order_by(TrafficRecord.recorded_at.asc())
        .all()
    )

    if len(records) < 10:
        return {
            "road_id": road_id,
            "status": "insufficient_data",
            "message": "At least 10 historical records are required for a preliminary chronological evaluation.",
            "sample_count": 0,
            "metrics": None,
        }

    frame = pd.DataFrame([
        {
            "road_id": row.road_id,
            "hour": row.recorded_at.hour,
            "day_of_week": row.recorded_at.weekday(),
            "vehicle_count": row.vehicle_count,
            "density": row.density,
            "actual": str(row.congestion_level).upper(),
        }
        for row in records
    ])

    split_index = int(len(frame) * 0.8)
    train_frame = frame.iloc[:split_index]
    test_frame = frame.iloc[split_index:]

    if test_frame.empty or train_frame["actual"].nunique() < 2:
        return {
            "road_id": road_id,
            "status": "insufficient_data",
            "message": "The chronological split does not contain enough class variation for evaluation.",
            "sample_count": len(test_frame),
            "metrics": None,
        }

    features = [
        "road_id",
        "hour",
        "day_of_week",
        "vehicle_count",
        "density",
    ]

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(train_frame[features], train_frame["actual"])

    actual = test_frame["actual"].to_numpy()
    predicted = model.predict(test_frame[features])

    precision, recall, f1, _ = precision_recall_fscore_support(
        actual,
        predicted,
        average="weighted",
        zero_division=0,
    )

    return {
        "road_id": road_id,
        "status": "preliminary_chronological_holdout",
        "message": "PRELIMINARY ONLY: A temporary model is trained on the first 80% of this road's records and evaluated on the last 20%. Congestion labels may be derived from density thresholds, and density is included among the model features; therefore, scores may reflect label leakage rather than genuine forecasting ability. Do not interpret these metrics as validated predictive accuracy.",
        "sample_count": len(test_frame),
        "metrics": {
            "accuracy": round(float(accuracy_score(actual, predicted)), 4),
            "weighted_precision": round(float(precision), 4),
            "weighted_recall": round(float(recall), 4),
            "weighted_f1": round(float(f1), 4),
        },
    }


def build_recommendations(db: Session, road_id: int):
    road = db.query(Road).filter(Road.id == road_id).first()
    if road is None:
        raise ValueError(f"Road {road_id} was not found.")

    records = (
        db.query(TrafficRecord)
        .filter(TrafficRecord.road_id == road_id)
        .order_by(TrafficRecord.recorded_at.desc())
        .limit(24)
        .all()
    )

    if not records:
        raise ValueError(f"No traffic records found for road {road_id}.")

    latest = records[0]
    observed = str(latest.congestion_level).upper()
    density = float(latest.density)

    try:
        prediction_service.load_model()
        prediction = prediction_service.predict_congestion(
            db=db,
            road_id=road_id,
            prediction_time=latest.recorded_at,
        )
        predicted = str(prediction["predicted_level"]).upper()
        model_version = prediction.get("model_version")
    except Exception:
        predicted = None
        model_version = None

    items = []

    if observed == "HIGH" or density >= 0.80 or predicted == "HIGH":
        items.append({
            "priority": "HIGH",
            "title": "Investigate and manage congestion",
            "reason": "Recent observations or the model indicate heavy congestion.",
            "suggested_action": "Verify current conditions, check for incidents, and coordinate signal timing with the traffic control team.",
            "road_id": road_id,
            "road_name": road.name,
            "basis": "traffic observations and available prediction",
        })
    elif observed == "MEDIUM" or density >= 0.50 or predicted == "MEDIUM":
        items.append({
            "priority": "MEDIUM",
            "title": "Monitor traffic buildup",
            "reason": "Recent traffic conditions indicate moderate congestion.",
            "suggested_action": "Monitor the corridor and review signal timing and queue lengths before making changes.",
            "road_id": road_id,
            "road_name": road.name,
            "basis": "traffic observations and available prediction",
        })
    else:
        items.append({
            "priority": "LOW",
            "title": "Continue routine monitoring",
            "reason": "Recent records indicate relatively low congestion.",
            "suggested_action": "Continue monitoring and reassess if vehicle counts or density rise.",
            "road_id": road_id,
            "road_name": road.name,
            "basis": "traffic observations and available prediction",
        })

    return {
        "road_id": road_id,
        "road_name": road.name,
        "observed_level": observed,
        "observed_density": round(density, 3),
        "predicted_level": predicted,
        "model_version": model_version,
        "record_count": len(records),
        "recommendations": items,
        "generated_by": "rule_based",
        "disclaimer": "These are decision-support suggestions, not validated traffic-control interventions. Review live conditions and local constraints before acting.",
    }
