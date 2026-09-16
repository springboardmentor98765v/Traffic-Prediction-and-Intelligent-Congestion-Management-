import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_predict_congestion_endpoint():
    response = requests.get(f"{BASE_URL}/api/v1/predict/congestion?road_id=R001")
    assert response.status_code == 200
    data = response.json()
    assert data["road_id"] == "R001"
    assert data["generated_by"] == "heuristic-v0"
    assert "predicted_level" in data
    assert data["predicted_level"] in ["Low", "Medium", "High"]
    assert "confidence" in data
    assert data["confidence"] == 0.80


def test_predict_live_endpoint():
    response = requests.get(f"{BASE_URL}/api/v1/predict/live")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) >= 5
