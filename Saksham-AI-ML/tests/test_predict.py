"""
Milestone 2 Day 6: Unit Test Suite & Latency Verification.
Covers:
- GET /predict/congestion (classification & metadata)
- GET /predict/delay (delay estimation & rush-hour flag)
- GET /predict/peak-hours (rush window heuristics)
- POST /predict/routes/rank (congestion-aware multi-route ranking)
- Latency threshold verification (< 1000ms response time)
"""
import time
from fastapi.testclient import TestClient
from ai_engine.main import app

client = TestClient(app)


def test_predict_congestion_endpoint():
    res = client.get("/predict/congestion?road_id=1&density=0.85&vehicle_count=120")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "1"
    assert data["predicted_level"] in ["HIGH", "SEVERE"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["model_version"] == "model-v1"
    assert data["data_source"] == "trained-random-forest"


def test_predict_delay_endpoint():
    res = client.get("/predict/delay?road_id=2&density=0.15&vehicle_count=20&time=2026-09-16T02:00:00")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "2"
    assert data["estimated_delay_minutes"] >= 0.0
    assert data["is_rush_hour"] is False


def test_peak_hours_endpoint():
    # Peak hour verification (e.g., 9 AM)
    res_peak = client.get("/predict/peak-hours?hour=9")
    assert res_peak.status_code == 200
    assert res_peak.json()["is_peak"] is True

    # Non-peak verification (e.g., 2 PM)
    res_off = client.get("/predict/peak-hours?hour=14")
    assert res_off.status_code == 200
    assert res_off.json()["is_peak"] is False


def test_route_ranking_logic():
    payload = {
        "candidate_routes": [
            {
                "route_id": "Route_A_Congested",
                "segments": [
                    {"road_id": "1", "base_duration_min": 12.0, "density": 0.90, "vehicle_count": 130}
                ],
            },
            {
                "route_id": "Route_B_Clear",
                "segments": [
                    {"road_id": "2", "base_duration_min": 14.0, "density": 0.20, "vehicle_count": 25}
                ],
            },
        ]
    }
    res = client.post("/predict/routes/rank", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_routes_evaluated"] == 2
    assert len(data["ranked_routes"]) == 2

    # Clearer route must be ranked 1 due to lower total effective ETA
    top_route = data["ranked_routes"][0]
    assert top_route["route_id"] == "Route_B_Clear"
    assert top_route["rank"] == 1
    assert top_route["is_recommended"] is True


def test_prediction_latency_sla():
    # Ensure inference latency is well under the 1-2 second target
    start_time = time.perf_counter()
    res = client.get("/predict/congestion?road_id=5&density=0.6&vehicle_count=70")
    elapsed_time = time.perf_counter() - start_time

    assert res.status_code == 200
    assert elapsed_time < 1.0, f"Inference exceeded 1.0s target SLA: {elapsed_time:.3f}s"