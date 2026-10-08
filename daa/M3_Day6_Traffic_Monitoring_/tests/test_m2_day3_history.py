import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
import main


def test_history_endpoint(monkeypatch):
    expected = {"count": 1, "data": [{"road_id": "R001"}]}
    monkeypatch.setattr(main, "get_traffic_history", lambda *args: expected)
    response = TestClient(main.app).get("/api/v1/traffic/history?road_id=R001")
    assert response.status_code == 200
    assert response.json() == expected


def test_history_limit_validation():
    response = TestClient(main.app).get("/api/v1/traffic/history?limit=0")
    assert response.status_code == 400


def test_aggregate_endpoint(monkeypatch):
    expected = {"interval": "day", "count": 1, "data": [{"road_id": "R001"}]}
    monkeypatch.setattr(main, "get_traffic_aggregate", lambda *args: expected)
    response = TestClient(main.app).get("/api/v1/traffic/aggregate?road_id=R001&interval=day")
    assert response.status_code == 200
    assert response.json() == expected


def test_aggregate_invalid_interval(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_traffic_aggregate",
        lambda *args: (_ for _ in ()).throw(ValueError("interval must be 'hour' or 'day'")),
    )
    response = TestClient(main.app).get("/api/v1/traffic/aggregate?interval=week")
    assert response.status_code == 400
