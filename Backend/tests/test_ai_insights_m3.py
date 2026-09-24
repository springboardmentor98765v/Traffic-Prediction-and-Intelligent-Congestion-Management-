import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_detect_anomalies():
    res = client.get("/api/v1/ai/anomalies?auto_alert=false")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    anom = data[0]
    assert "road_id" in anom
    assert "time" in anom
    assert "expected_level" in anom
    assert "observed_level" in anom
    assert anom["flagged_as"] == "possible_incident"


def test_ai_recommendations_general():
    res = client.get("/api/v1/ai/recommendations")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    for item in data:
        assert "recommendation_text" in item
        assert "based_on" in item
        assert len(item["recommendation_text"]) > 10


def test_ai_recommendations_road_specific():
    res = client.get("/api/v1/ai/recommendations?road_id=R002")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    rec = data[0]
    assert "recommendation_text" in rec
    assert "based_on" in rec


def test_anomalies_auto_trigger_alerts():
    # Calling with auto_alert=true should generate accident alerts
    res = client.get("/api/v1/ai/anomalies?auto_alert=true")
    assert res.status_code == 200

    # Verify that an accident alert was logged in the alerts system
    alerts_res = client.get("/api/v1/alerts/active")
    assert alerts_res.status_code == 200
    types = [a["type"] for a in alerts_res.json()]
    assert "accident" in types
