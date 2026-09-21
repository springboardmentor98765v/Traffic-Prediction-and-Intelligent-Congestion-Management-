import importlib.util
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
AI_ROOT = ROOT / "services" / "ai-engine"
AI_SPEC = importlib.util.spec_from_file_location("backend_ai_main", AI_ROOT / "app" / "main.py")
AI_MODULE = importlib.util.module_from_spec(AI_SPEC)
sys.modules[AI_SPEC.name] = AI_MODULE
AI_SPEC.loader.exec_module(AI_MODULE)


def test_backend_ai_prediction_uses_ml_v2_and_external_data():
    client = TestClient(AI_MODULE.app)
    response = client.get("/api/v1/predict/congestion?road_id=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["road_id"] == "1"
    assert payload["model_version"] == "ml-v2"
    assert payload["predicted_level"] in {"LOW", "MEDIUM", "HIGH", "SEVERE"}


def test_backend_ai_traffic_endpoints_use_five_external_roads():
    client = TestClient(AI_MODULE.app)
    response = client.get("/api/v1/traffic/live")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 5
    assert {"road_id", "road_name", "vehicle_count", "density", "avg_speed_kmph", "congestion_level"}.issubset(payload[0])


def test_backend_ai_delay_and_route_ranking_support_four_classes():
    client = TestClient(AI_MODULE.app)
    delay = client.get("/api/v1/predict/delay?road_id=1&distance_km=2")
    ranking = client.post(
        "/api/v1/route/rank",
        json={"routes": [{"route_id": "route-1", "distance_km": 2, "roads": ["1", "2"]}]},
    )

    assert delay.status_code == 200
    assert delay.json()["model_version"] == "ml-v2"
    assert ranking.status_code == 200
    assert ranking.json()[0]["predicted_congestion"] in {"LOW", "MEDIUM", "HIGH", "SEVERE"}


def test_gateway_owns_route_rank_proxy():
    gateway_path = ROOT / "services" / "gateway" / "app" / "main.py"
    source = gateway_path.read_text(encoding="utf-8")

    assert '"/api/v1/route/rank"' in source
    assert 'PREDICTION_SERVICE_URL, "api/v1/route/rank"' in source
