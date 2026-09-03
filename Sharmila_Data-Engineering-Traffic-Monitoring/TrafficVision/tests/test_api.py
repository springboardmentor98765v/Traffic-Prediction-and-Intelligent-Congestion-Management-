import sys
from pathlib import Path

# Add the project root to Python's path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "TrafficVision API is running"


def test_live_traffic():
    response = client.get("/traffic/live")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_traffic_density():
    response = client.get("/traffic/density")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_traffic_utilization():
    response = client.get("/traffic/utilization")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_congestion_history():
    response = client.get("/traffic/congestion/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_traffic_by_road():
    response = client.get("/traffic/road/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)