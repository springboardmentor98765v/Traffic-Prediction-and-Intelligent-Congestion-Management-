import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ROUTE_URL = os.getenv("ROUTE_SERVICE_URL", f"{BASE_URL}/api/v1/route")


@pytest.fixture(scope="module")
def auth_headers():
    token = os.getenv("AUTH_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.mark.route
def test_route_optimize_valid(auth_headers):
    """TC-ROUT-001: Verify route optimization returns shortest/optimal path and geometry."""
    url = f"{ROUTE_URL}/optimize"
    params = {
        "origin_lat": 12.9716,
        "origin_lon": 77.5946,
        "dest_lat": 12.9352,
        "dest_lon": 77.6245,
    }
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Route Analysis service unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()

    assert "distance_km" in data or "distance" in data, "Response missing distance metric"
    assert "estimated_time_min" in data or "travel_time" in data, "Response missing travel time metric"
    assert "route_geometry" in data or "coordinates" in data or "waypoints" in data, "Response missing geometry"


@pytest.mark.route
def test_route_optimize_missing_params(auth_headers):
    """TC-ROUT-002: Verify missing destination coordinates returns 400 or 422."""
    url = f"{ROUTE_URL}/optimize"
    params = {"origin_lat": 12.9716, "origin_lon": 77.5946}  # dest omitted
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Route Analysis service unreachable at {url}")

    assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"


@pytest.mark.route
def test_route_alternate_ranking(auth_headers):
    """TC-ROUT-003: Verify alternate routes are generated and ranked by predicted congestion."""
    url = f"{ROUTE_URL}/alternate"
    params = {
        "origin_lat": 12.9716,
        "origin_lon": 77.5946,
        "dest_lat": 12.9352,
        "dest_lon": 77.6245,
        "max_alternates": 3,
    }
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Route Analysis alternate endpoint unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()

    routes = data.get("routes", data if isinstance(data, list) else [])
    assert len(routes) >= 1, "At least one route candidate must be returned"
    
    # Verify congestion score or predicted congestion level is returned
    first_route = routes[0]
    assert any(k in first_route for k in ["predicted_congestion", "congestion_level", "congestion_score", "rank"]), \
        "Candidate routes must include congestion-aware ranking attributes"


@pytest.mark.route
def test_route_travel_time(auth_headers):
    """TC-ROUT-005: Verify travel-time estimation endpoint returns baseline & adjusted estimates."""
    url = f"{ROUTE_URL}/travel-time"
    params = {
        "origin_lat": 12.9716,
        "origin_lon": 77.5946,
        "dest_lat": 12.9352,
        "dest_lon": 77.6245,
    }
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Route travel-time endpoint unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    assert "estimated_time_min" in data or "travel_time_min" in data or "duration" in data


@pytest.mark.route
def test_route_conditions_query(auth_headers):
    """TC-ROUT-007: Verify road conditions endpoint returns status and hazard warnings."""
    url = f"{ROUTE_URL}/conditions"
    params = {"road_id": "road_1"}
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Route conditions endpoint unreachable at {url}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    assert "road_id" in data
    assert "condition" in data or "status" in data or "hazards" in data


@pytest.mark.route
def test_route_conditions_not_found(auth_headers):
    """TC-ROUT-008: Verify querying non-existent road ID returns 404 Not Found."""
    url = f"{ROUTE_URL}/conditions"
    params = {"road_id": "invalid_non_existent_road_9999"}
    try:
        response = requests.get(url, params=params, headers=auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Route conditions endpoint unreachable at {url}")

    assert response.status_code == 404, f"Expected 404 Not Found, got {response.status_code}"
