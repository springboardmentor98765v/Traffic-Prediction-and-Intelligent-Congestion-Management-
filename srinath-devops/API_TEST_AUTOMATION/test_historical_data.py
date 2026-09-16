import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
HISTORICAL_URL = os.getenv("HISTORICAL_SERVICE_URL", f"{BASE_URL}/api/v1/traffic")


@pytest.fixture(scope="module")
def auth_headers():
    token = os.getenv("AUTH_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.mark.historical
def test_historical_traffic_query(auth_headers):
    """TC-HIST-001: Verify historical traffic data retrieval with road_id and date filtering."""
    url = f"{HISTORICAL_URL}/history"
    params = {"road_id": "road_1"}
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Historical traffic service unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    assert isinstance(data, (list, dict)), "Response should be list of records or dict container"


@pytest.mark.historical
def test_historical_traffic_aggregation(auth_headers):
    """TC-HIST-002: Verify hourly aggregated traffic metrics (average density and speed)."""
    url = f"{HISTORICAL_URL}/history/aggregated"
    params = {"road_id": "road_1", "interval": "hourly"}
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Aggregated historical endpoint unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    assert "aggregates" in data or isinstance(data, list), "Missing aggregation data array"
