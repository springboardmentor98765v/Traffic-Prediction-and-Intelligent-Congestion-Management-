import os
import time
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
PREDICTION_URL = os.getenv("PREDICTION_SERVICE_URL", f"{BASE_URL}/api/v1/predict")


@pytest.fixture(scope="module")
def auth_headers():
    """Retrieve auth token or mock bearer header for testing."""
    token = os.getenv("AUTH_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.mark.prediction
def test_predict_congestion_valid(auth_headers):
    """TC-PRED-001: Verify congestion prediction returns valid response and trained model version."""
    url = f"{PREDICTION_URL}/congestion"
    params = {"road_id": "road_1"}
    
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Prediction service unreachable at {url} (Dependency Blocked)")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()

    assert "road_id" in data, "Response missing 'road_id'"
    assert "predicted_level" in data, "Response missing 'predicted_level'"
    assert data["predicted_level"] in ["Low", "Medium", "High", "LOW", "MEDIUM", "HIGH"]
    assert "confidence" in data, "Response missing 'confidence'"
    assert 0.0 <= float(data["confidence"]) <= 1.0, f"Invalid confidence value: {data['confidence']}"
    
    # Milestone 2 acceptance requirement: Verify model version
    if "model_version" in data:
        assert data["model_version"] != "heuristic-v0", "Milestone 1 heuristic placeholder detected! Real model required."
    elif "generated_by" in data:
        assert data["generated_by"] != "heuristic-v0", "Heuristic stub 'heuristic-v0' returned instead of real model!"


@pytest.mark.prediction
def test_predict_congestion_missing_param(auth_headers):
    """TC-PRED-003: Verify missing road_id returns 422 Unprocessable Entity."""
    url = f"{PREDICTION_URL}/congestion"
    try:
        response = requests.get(url, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Prediction service unreachable at {url}")

    assert response.status_code in [400, 422], f"Expected 400 or 422 for missing parameter, got {response.status_code}"


@pytest.mark.prediction
def test_predict_congestion_invalid_hour(auth_headers):
    """TC-PRED-004: Verify invalid hour parameter (>23) returns 400 or 422 error."""
    url = f"{PREDICTION_URL}/congestion"
    params = {"road_id": "road_1", "hour": 25}
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Prediction service unreachable at {url}")

    assert response.status_code in [400, 422], f"Expected 400/422 for hour=25, got {response.status_code}"


@pytest.mark.prediction
def test_predict_peak_hours_valid(auth_headers):
    """TC-PRED-005: Verify peak-hours forecast returns 24-hour distribution and peak windows."""
    url = f"{PREDICTION_URL}/peak-hours"
    params = {"road_id": "road_1"}
    
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Prediction peak-hours endpoint unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()

    assert "road_id" in data
    assert "hourly_forecast" in data or "peak_windows" in data, "Response missing forecast details"


@pytest.mark.prediction
def test_predict_delay_valid(auth_headers):
    """TC-PRED-007: Verify delay estimation endpoint computes expected delay and total duration."""
    url = f"{PREDICTION_URL}/delay"
    params = {"road_id": "road_1", "baseline_travel_time_min": 20}
    
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Prediction delay endpoint unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()

    assert "road_id" in data
    assert "predicted_delay_min" in data or "predicted_delay_seconds" in data, "Missing delay estimate field"


@pytest.mark.latency
def test_prediction_latency_sanity(auth_headers):
    """TC-PRED-009: Verify prediction latency meets SRS target (~1-2 seconds)."""
    url = f"{PREDICTION_URL}/congestion"
    params = {"road_id": "road_1"}

    try:
        start_time = time.time()
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
        elapsed_seconds = time.time() - start_time
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Prediction service unreachable at {url}")

    assert response.status_code == 200
    assert elapsed_seconds <= 2.0, f"Prediction latency {elapsed_seconds:.2f}s exceeded 2.0s target!"
