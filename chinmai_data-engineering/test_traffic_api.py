import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
import main


def test_root_endpoint(monkeypatch):
    client = TestClient(main.app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "Traffic Monitoring Service"


def test_live_traffic_endpoint(monkeypatch):
    expected = [
        {
            "road_id": "R001",
            "vehicle_count": 28,
            "density": 5.6,
            "congestion_level": "Low",
            "updated_at": "2026-08-26T22:00:00",
        }
    ]

    monkeypatch.setattr(main, "get_live_traffic", lambda: expected)

    client = TestClient(main.app)
    response = client.get("/api/v1/traffic/live")

    assert response.status_code == 200
    assert response.json() == expected


def test_density_endpoint(monkeypatch):
    expected = {
        "total_roads": 6,
        "average_density": 6.62,
        "maximum_density": 11.33,
        "minimum_density": 0.22,
        "high_congestion_roads": 0,
        "severe_congestion_roads": 0,
        "total_vehicle_count": 137,
    }

    monkeypatch.setattr(main, "get_density_summary", lambda: expected)

    client = TestClient(main.app)
    response = client.get("/api/v1/traffic/density")

    assert response.status_code == 200
    assert response.json() == expected


def test_unknown_road_returns_404(monkeypatch):
    monkeypatch.setattr(main, "get_road_traffic", lambda road_id: None)

    client = TestClient(main.app)
    response = client.get("/api/v1/traffic/road/R999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Road 'R999' not found"
