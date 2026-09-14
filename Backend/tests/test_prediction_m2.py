import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_predict_congestion_model_v1():
    res = client.get("/api/v1/predict/congestion?road_id=R001")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert data["model_version"] == "model-v1"
    assert data["predicted_level"] in ["Low", "Medium", "High"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert "current_density" in data


def test_predict_peak_hours():
    res = client.get("/api/v1/predict/peak-hours?road_id=R001")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert "peak_windows" in data
    assert len(data["peak_windows"]) >= 1
    for win in data["peak_windows"]:
        assert "start" in win
        assert "end" in win
        assert "severity" in win


def test_predict_peak_hours_404():
    res = client.get("/api/v1/predict/peak-hours?road_id=INVALID_ROAD")
    assert res.status_code == 404


def test_predict_delay():
    res = client.get("/api/v1/predict/delay?road_id=R002")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R002"
    assert "estimated_delay_minutes" in data
    assert data["estimated_delay_minutes"] >= 0.0
    assert "free_flow_speed_kmh" in data
    assert "congested_speed_kmh" in data
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_report_json():
    res = client.get("/api/v1/predict/report?road_id=R001&format=json")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert data["model_version"] == "model-v1"
    assert "peak_windows" in data
    assert "hourly_forecast" in data
    assert len(data["hourly_forecast"]) == 24
    assert "estimated_delay_minutes" in data


def test_predict_report_csv():
    res = client.get("/api/v1/predict/report?road_id=R001&format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment; filename=traffic_prediction_R001.csv" in res.headers["content-disposition"]
    text = res.text
    assert "Road ID" in text
    assert "R001" in text
    assert "Hourly Forecast" in text or "Hour" in text
