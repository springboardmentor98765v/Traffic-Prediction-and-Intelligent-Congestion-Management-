import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.predict import predict_congestion


def test_low_congestion():
    level, reason = predict_congestion(
        vehicle_count=40,
        density=8.0,
        avg_speed_kmph=45,
    )

    assert level == "Low"
    assert "normal" in reason.lower()


def test_medium_congestion():
    level, reason = predict_congestion(
        vehicle_count=70,
        density=15.0,
        avg_speed_kmph=30,
    )

    assert level == "Medium"
    assert "moderate" in reason.lower()


def test_high_congestion():
    level, reason = predict_congestion(
        vehicle_count=110,
        density=25.0,
        avg_speed_kmph=15,
    )

    assert level == "High"
    assert "high traffic density" in reason.lower()


def test_boundary_density_10():
    level, _ = predict_congestion(
        vehicle_count=50,
        density=10,
        avg_speed_kmph=35,
    )

    assert level == "Medium"


def test_boundary_density_20():
    level, _ = predict_congestion(
        vehicle_count=90,
        density=20,
        avg_speed_kmph=20,
    )

    assert level == "High"
