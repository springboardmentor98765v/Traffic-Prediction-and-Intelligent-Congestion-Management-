import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.predict import predict_congestion


def test_low_traffic_prediction():
    level, confidence = predict_congestion(
        vehicle_count=40,
        density=8.0,
        avg_speed_kmph=45.0,
        road_capacity=100.0,
        road_length_km=5.0,
        hour=10,
        day_of_week=1,
        is_weekend=0,
        road_id="R001",
    )

    assert level in {"Low", "Medium", "High", "Severe"}
    assert 0.0 <= confidence <= 1.0


def test_medium_traffic_prediction():
    level, confidence = predict_congestion(
        vehicle_count=70,
        density=15.0,
        avg_speed_kmph=30.0,
        road_capacity=100.0,
        road_length_km=5.0,
        hour=18,
        day_of_week=1,
        is_weekend=0,
        road_id="R001",
    )

    assert level in {"Low", "Medium", "High", "Severe"}
    assert 0.0 <= confidence <= 1.0


def test_high_traffic_prediction():
    level, confidence = predict_congestion(
        vehicle_count=110,
        density=25.0,
        avg_speed_kmph=15.0,
        road_capacity=100.0,
        road_length_km=5.0,
        hour=18,
        day_of_week=1,
        is_weekend=0,
        road_id="R001",
    )

    assert level in {"Low", "Medium", "High", "Severe"}
    assert 0.0 <= confidence <= 1.0


def test_prediction_returns_valid_confidence():
    level, confidence = predict_congestion(
        vehicle_count=50,
        density=10.0,
        avg_speed_kmph=35.0,
        road_capacity=100.0,
        road_length_km=5.0,
        hour=12,
        day_of_week=2,
        is_weekend=0,
        road_id="R001",
    )

    assert isinstance(level, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
