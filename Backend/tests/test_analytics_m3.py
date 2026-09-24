import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_traffic_trends_day():
    res = client.get("/api/v1/analytics/trends?road_id=R001&range=day")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert data["range"] == "day"
    assert "points" in data
    assert len(data["points"]) == 24
    p = data["points"][0]
    assert "period" in p
    assert "avg_congestion" in p
    assert "avg_speed" in p
    assert "avg_density" in p


def test_traffic_trends_week():
    res = client.get("/api/v1/analytics/trends?road_id=R002&range=week")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R002"
    assert data["range"] == "week"
    assert "points" in data
    assert len(data["points"]) == 7
    days = [p["period"] for p in data["points"]]
    assert "Monday" in days
    assert "Friday" in days


def test_traffic_trends_invalid_road():
    res = client.get("/api/v1/analytics/trends?road_id=INVALID_999&range=day")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_congestion_heatmap_day():
    res = client.get("/api/v1/analytics/heatmap?range=day")
    assert res.status_code == 200
    data = res.json()
    assert data["range"] == "day"
    assert "roads" in data
    assert len(data["roads"]) >= 5
    assert "time_buckets" in data
    assert len(data["time_buckets"]) == 6
    assert "values" in data
    assert len(data["values"]) == len(data["roads"])
    for row in data["values"]:
        assert len(row) == len(data["time_buckets"])
        for val in row:
            assert isinstance(val, (int, float))
            assert 0.0 <= val <= 1.0


def test_congestion_heatmap_week():
    res = client.get("/api/v1/analytics/heatmap?range=week")
    assert res.status_code == 200
    data = res.json()
    assert data["range"] == "week"
    assert len(data["time_buckets"]) == 7
    assert len(data["values"]) == len(data["roads"])


def test_historical_report_csv():
    res = client.get("/api/v1/analytics/reports?range=week&format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment; filename=traffic_report_week.csv" in res.headers["content-disposition"]
    text = res.text
    assert "reading_id,road_id,road_name,timestamp" in text
    lines = text.strip().split("\n")
    assert len(lines) > 5


def test_historical_report_json():
    res = client.get("/api/v1/analytics/reports?range=week&format=json")
    assert res.status_code == 200
    data = res.json()
    assert "total_records" in data
    assert data["total_records"] > 0
    assert "total_roads" in data
    assert "average_city_speed" in data
    assert "average_city_density" in data
    assert "peak_congestion_road" in data
    assert "records" in data
