import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_predict_congestion_default():
    res = client.get("/api/v1/predict/congestion?road_id=R001")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert data["generated_by"] in ["model-v1", "heuristic-v0"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["predicted_level"] in ["Low", "Medium", "High"]
    assert "current_density" in data


def test_predict_congestion_thresholds_and_peak_hours():
    # Low density (10), off-peak (14:00) -> Low
    res_low = client.get("/api/v1/predict/congestion?road_id=R001&density=10&hour=14")
    assert res_low.status_code == 200
    assert res_low.json()["predicted_level"] == "Low"

    # Low density (10), peak hour (8:00) -> Low elevated to Medium
    res_peak = client.get("/api/v1/predict/congestion?road_id=R001&density=10&hour=8")
    assert res_peak.status_code == 200
    assert res_peak.json()["predicted_level"] == "Medium"

    # High density (75), any hour -> High
    res_high = client.get("/api/v1/predict/congestion?road_id=R001&density=75&hour=14")
    assert res_high.status_code == 200
    assert res_high.json()["predicted_level"] == "High"


def test_predict_unknown_road_404():
    res = client.get("/api/v1/predict/congestion?road_id=UNKNOWN_99")
    assert res.status_code == 404


def test_predict_live_all_roads():
    res = client.get("/api/v1/predict/live")
    assert res.status_code == 200
    data = res.json()
    assert "predictions" in data
    assert len(data["predictions"]) >= 5
    for p in data["predictions"]:
        assert p["generated_by"] in ["model-v1", "heuristic-v0"]
