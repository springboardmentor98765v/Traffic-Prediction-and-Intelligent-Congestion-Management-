import sys
from pathlib import Path

from fastapi.testclient import TestClient

AI_ENGINE_DIR = Path(__file__).resolve().parents[1]
if str(AI_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_DIR))

from app import app


client = TestClient(app)


def test_ai_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "ai-insights"


def test_recommendations_endpoint_returns_contract_fields():
    response = client.get("/api/v1/ai/recommendations", params={"road_id": "R001"})
    assert response.status_code == 200, response.text
    recommendations = response.json()
    assert recommendations
    assert all(item["road_id"] == "R001" for item in recommendations)
    assert all(item["recommendation_text"] and item["based_on"] for item in recommendations)


def test_recommendations_endpoint_rejects_unknown_road():
    response = client.get("/api/v1/ai/recommendations", params={"road_id": "R999"})
    assert response.status_code == 404


def test_anomalies_endpoint_filters_to_requested_road():
    response = client.get("/api/v1/ai/anomalies", params={"road_id": "R001"})
    assert response.status_code == 200, response.text
    assert all(item["road_id"] == "R001" for item in response.json())
