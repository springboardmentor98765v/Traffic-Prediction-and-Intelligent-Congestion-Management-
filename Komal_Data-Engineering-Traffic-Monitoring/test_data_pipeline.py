import pytest
import os
import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR))

from ingestion import get_congestion_level
from congestion_tracker import track_congestion
from road_analysis import analyze_road_utilization
from cache import set_cache, get_cache


def test_congestion_level_thresholds():
    # Low: < 20
    assert get_congestion_level(0) == "Low"
    assert get_congestion_level(15.5) == "Low"
    assert get_congestion_level(19.9) == "Low"

    # Medium: 20 to 50
    assert get_congestion_level(20.0) == "Medium"
    assert get_congestion_level(35.0) == "Medium"
    assert get_congestion_level(50.0) == "Medium"

    # High: > 50
    assert get_congestion_level(50.1) == "High"
    assert get_congestion_level(85.0) == "High"
    assert get_congestion_level(100.0) == "High"


def test_road_utilization_analysis():
    results = analyze_road_utilization()
    assert isinstance(results, list)
    assert len(results) >= 5

    road_ids = [r["road_id"] for r in results]
    for expected_id in ["R001", "R002", "R003", "R004", "R005"]:
        assert expected_id in road_ids

    first = results[0]
    assert "total_vehicles" in first
    assert "average_speed" in first
    assert "average_density" in first
    assert "congestion" in first
    assert first["congestion"] in ["Low", "Medium", "High"]


def test_congestion_tracker():
    history = track_congestion()
    assert isinstance(history, dict)
    assert "R001" in history
    assert len(history["R001"]) > 0
    first_record = history["R001"][0]
    assert "timestamp" in first_record
    assert "congestion" in first_record
    assert "density" in first_record
    assert "avg_speed" in first_record


def test_cache_fallback():
    test_key = "unit_test_key"
    test_data = {"road": "R001", "status": "active"}
    set_cache(test_key, test_data, expiry=10)
    retrieved = get_cache(test_key)
    assert retrieved == test_data
