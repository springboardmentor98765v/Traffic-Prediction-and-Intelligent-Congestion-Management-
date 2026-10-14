import pytest
from fastapi.testclient import TestClient
from ai_engine.main import app, is_rush_hour, predict_ml_congestion
from datetime import datetime

client = TestClient(app)


def test_health_endpoint():
    """Verify service health and model loading."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ml_model_loaded" in data


def test_predict_congestion_contract():
    """Verify standard prediction response schema and valid classification values."""
    response = client.get("/api/v1/predict/congestion?road_id=1")
    assert response.status_code == 200
    data = response.json()
    
    assert data["road_id"] == "1"
    assert data["predicted_level"] in ["LOW", "MEDIUM", "HIGH", "SEVERE"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert "explanation" in data
    assert "density_used" in data
    assert isinstance(data["peak_hour"], bool)
    assert data["data_source"] in ["live-stream", "fallback-baseline"]


def test_predict_congestion_string_identifier():
    """Verify endpoint accepts string road identifiers like R001 without crashing."""
    response = client.get("/api/v1/predict/congestion?road_id=R001")
    assert response.status_code == 200
    data = response.json()
    assert data["road_id"] == "R001"


def test_ml_prediction_function_direct():
    """Verify direct ML prediction output ranges."""
    level, confidence, explanation = predict_ml_congestion(
        density=0.85, vehicle_count=180.0, avg_speed_kmph=15.0
    )
    assert level in ["LOW", "MEDIUM", "HIGH", "SEVERE"]
    assert 0.0 <= confidence <= 1.0
    assert len(explanation) > 0


def test_rush_hour_detection():
    """Verify peak rush hour logic."""
    morning_rush = datetime(2026, 9, 3, 9, 30)
    assert is_rush_hour(morning_rush) is True

    evening_rush = datetime(2026, 9, 3, 18, 15)
    assert is_rush_hour(evening_rush) is True

    off_peak = datetime(2026, 9, 3, 14, 0)
    assert is_rush_hour(off_peak) is False