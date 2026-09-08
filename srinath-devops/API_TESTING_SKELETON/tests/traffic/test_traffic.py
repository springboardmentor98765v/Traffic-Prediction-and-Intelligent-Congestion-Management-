import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_traffic_live_endpoint():
    response = requests.get(f"{BASE_URL}/api/v1/traffic/live")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    first_road = data[0]
    assert "road_id" in first_road
    assert "density" in first_road
    assert "congestion_level" in first_road


def test_traffic_road_detail_endpoint():
    response = requests.get(f"{BASE_URL}/api/v1/traffic/road/R001")
    assert response.status_code == 200
    data = response.json()
    assert data["road_id"] == "R001"
    assert "history" in data


def test_traffic_density_metrics():
    response = requests.get(f"{BASE_URL}/api/v1/traffic/density")
    assert response.status_code == 200
    data = response.json()
    assert "average_density" in data
    assert "total_roads" in data


def test_traffic_endpoint_not_found():
    response = requests.get(f"{BASE_URL}/api/v1/traffic/road/INVALID_CORRIDOR_999")
    assert response.status_code == 404
