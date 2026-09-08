import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_get_live_traffic():
    res = client.get("/api/v1/traffic/live")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 5

    road_ids = [r["road_id"] for r in data]
    assert "R001" in road_ids
    assert "R002" in road_ids

    first = data[0]
    for key in ["road_id", "name", "vehicle_count", "density", "congestion_level", "updated_at"]:
        assert key in first
        assert first[key] is not None


def test_get_road_detail_and_history():
    res = client.get("/api/v1/traffic/road/R001")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert data["name"] == "MG Road"
    assert "density" in data
    assert "vehicle_count" in data
    assert "history" in data
    assert isinstance(data["history"], list)


def test_get_unknown_road_returns_404():
    res = client.get("/api/v1/traffic/road/NON_EXISTENT")
    assert res.status_code == 404


def test_get_density_metrics():
    res = client.get("/api/v1/traffic/density")
    assert res.status_code == 200
    data = res.json()
    assert "average_density" in data
    assert "total_roads" in data
    assert data["total_roads"] >= 5
    assert "congested_roads" in data
    assert "timestamp" in data
