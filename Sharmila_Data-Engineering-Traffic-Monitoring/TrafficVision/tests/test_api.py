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
    
    
# Milestone 2 - Tests


def test_traffic_history():
    response = client.get(
        "/traffic/history",
        params={
            "road_id": 1,
            "start": "2026-01-01 00:00:00",
            "end": "2026-01-01 23:00:00"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if response.json():
        record = response.json()[0]

        assert "road_id" in record
        assert "timestamp" in record
        assert "vehicle_count" in record
        assert "density" in record
        assert "congestion_level" in record


def test_traffic_aggregate_hourly():
    response = client.get(
        "/traffic/aggregate",
        params={
            "road_id": 1,
            "start": "2026-01-01 00:00:00",
            "end": "2026-01-01 23:00:00",
            "interval": "hour"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_traffic_aggregate_daily():
    response = client.get(
        "/traffic/aggregate",
        params={
            "road_id": 1,
            "start": "2026-01-01 00:00:00",
            "end": "2026-01-07 23:00:00",
            "interval": "day"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_road_condition():
    response = client.get("/traffic/road-condition/1")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if response.json():
        condition = response.json()[0]

        assert "road_id" in condition
        assert "condition_type" in condition
        assert "description" in condition
        assert "is_active" in condition
        assert "updated_at" in condition


def test_clean_historical_dataset():
    import pandas as pd

    file_path = "traffic_history_clean.csv"

    df = pd.read_csv(file_path)

    assert len(df) > 0
    assert df["road_id"].notna().all()
    assert df["timestamp"].notna().all()
    assert df["vehicle_count"].notna().all()
    assert df["density"].notna().all()
    assert df["congestion_level"].notna().all()

    assert (df["vehicle_count"] >= 0).all()
    assert (df["density"] >= 0).all()

    assert df["congestion_level"].isin(
        ["Low", "Medium", "High"]
    ).all()

    assert not df.duplicated(
        subset=["road_id", "timestamp"]
    ).any()