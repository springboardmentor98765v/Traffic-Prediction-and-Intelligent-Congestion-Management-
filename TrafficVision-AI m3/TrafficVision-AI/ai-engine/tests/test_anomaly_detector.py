import sys
from pathlib import Path

import pytest


# Allow importing from ai-engine/src
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from anomaly_detector import AnomalyDetector


@pytest.fixture
def detector():
    return AnomalyDetector()


def test_thresholds_are_valid(detector):
    """Thresholds should be positive and correctly ordered."""

    assert detector.anomaly_threshold > 0
    assert detector.incident_threshold > 0

    assert detector.incident_threshold > detector.anomaly_threshold


def test_normal_observation(detector):
    """A normal historical observation should not be flagged."""

    result = detector.analyze(
        road_id="R001",
        timestamp="2026-07-27T00:00:00+05:30",
        vehicle_count=26,
        avg_speed_kmph=32.54,
        traffic_density=5.2,
    )

    assert result["anomaly_class"] == "normal"


def test_possible_incident_detection(detector):
    """A strong multi-signal deviation should be detected."""

    result = detector.analyze(
        road_id="R001",
        timestamp="2026-07-27T00:00:00+05:30",
        vehicle_count=54,
        avg_speed_kmph=13.13,
        traffic_density=10.7,
    )

    assert result["anomaly_class"] == "possible_incident"
    assert result["strong_signal_count"] >= 2
    assert result["anomaly_score"] >= detector.incident_threshold


def test_vehicle_deviation_increases_score(detector):
    """A large vehicle-count deviation should affect the anomaly score."""

    normal = detector.analyze(
        road_id="R001",
        timestamp="2026-07-27T00:00:00+05:30",
        vehicle_count=26,
        avg_speed_kmph=32.54,
        traffic_density=5.2,
    )

    abnormal = detector.analyze(
        road_id="R001",
        timestamp="2026-07-27T00:00:00+05:30",
        vehicle_count=80,
        avg_speed_kmph=32.54,
        traffic_density=5.2,
    )

    assert abnormal["anomaly_score"] > normal["anomaly_score"]


def test_speed_drop_increases_score(detector):
    """A major speed reduction should increase anomaly score."""

    normal = detector.analyze(
        road_id="R001",
        timestamp="2026-07-27T00:00:00+05:30",
        vehicle_count=26,
        avg_speed_kmph=32.54,
        traffic_density=5.2,
    )

    slow = detector.analyze(
        road_id="R001",
        timestamp="2026-07-27T00:00:00+05:30",
        vehicle_count=26,
        avg_speed_kmph=13.13,
        traffic_density=5.2,
    )

    assert slow["anomaly_score"] > normal["anomaly_score"]


def test_missing_baseline(detector):
    """Unknown road/time combinations should not crash."""

    result = detector.analyze(
        road_id="UNKNOWN_ROAD",
        timestamp="2026-07-27T00:00:00+05:30",
        vehicle_count=50,
        avg_speed_kmph=20,
        traffic_density=10,
    )

    assert result["anomaly_class"] == "unknown"
    assert "reason" in result