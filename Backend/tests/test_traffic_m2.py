import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_traffic_history_all():
    res = client.get("/api/v1/traffic/history")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    sample = data[0]
    assert "road_id" in sample
    assert "timestamp" in sample
    assert "vehicle_count" in sample
    assert "density" in sample
    assert "congestion_level" in sample


def test_traffic_history_filter_road():
    res = client.get("/api/v1/traffic/history?road_id=R001&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    for r in data:
        assert r["road_id"] == "R001"


def test_traffic_aggregate_hour():
    res = client.get("/api/v1/traffic/aggregate?road_id=R001&granularity=hour")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert data["granularity"] == "hour"
    assert "avg_density" in data
    assert "avg_vehicle_count" in data
    assert "avg_speed" in data
    assert "congestion_distribution" in data
    assert "total_readings" in data


def test_traffic_aggregate_day():
    res = client.get("/api/v1/traffic/aggregate?granularity=day")
    assert res.status_code == 200
    data = res.json()
    assert data["granularity"] == "day"
    assert "avg_density" in data


def test_traffic_road_condition_get():
    res = client.get("/api/v1/traffic/road-condition/R001")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert "status" in data
    assert "notes" in data


def test_traffic_road_condition_404():
    res = client.get("/api/v1/traffic/road-condition/NON_EXISTENT")
    assert res.status_code == 404
