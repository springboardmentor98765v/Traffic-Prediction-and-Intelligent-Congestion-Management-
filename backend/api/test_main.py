from datetime import datetime

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.main import (
    RouteRankingRequest,
    app,
    predict_congestion_api,
    predict_delay,
    predict_peak_hours,
    rank_routes,
)

client = TestClient(app)


def test_prediction_uses_latest_data_engineering_record():
    result = predict_congestion_api("1")

    assert result.road_id == "1"
    assert result.predicted_level in {"LOW", "MEDIUM", "HIGH", "SEVERE"}
    assert result.model_version == "ml-v2"
    assert result.density == 19.9


def test_prediction_accepts_live_observation():
    result = predict_congestion_api(
        "1",
        vehicle_count=80,
        average_speed=45,
        timestamp=datetime(2026, 9, 4, 8, 0),
    )

    assert result.road_id == "1"
    assert result.predicted_level in {"LOW", "MEDIUM", "HIGH", "SEVERE"}
    assert result.density == 0.4


def test_unknown_road_returns_not_found():
    with pytest.raises(HTTPException) as error:
        predict_congestion_api("UNKNOWN")

    assert error.value.status_code == 404


def test_peak_hours_and_delay_are_model_backed():
    peak_hours = predict_peak_hours("1")
    delay = predict_delay("1", distance_km=2)

    assert peak_hours.peak_windows == ["08:00-10:59", "17:00-19:59"]
    assert delay.predicted_level in {"LOW", "MEDIUM", "HIGH", "SEVERE"}
    assert delay.model_version == "ml-v2"
    assert delay.estimated_delay_minutes > 0


def test_route_ranking_prefers_less_congested_route():
    ranked = rank_routes(RouteRankingRequest(routes=[
        {"route_id": "first", "distance_km": 2, "roads": ["1"]},
        {"route_id": "second", "distance_km": 2, "roads": ["2"]},
    ]))

    assert len(ranked) == 2
    assert ranked[0].score <= ranked[1].score


def test_api_v1_live_traffic_endpoint():
    response = client.get("/api/v1/traffic/live")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert len(payload) == 5
    assert {"road_id", "road_name", "vehicle_count", "density", "avg_speed_kmph", "speed", "congestion_level", "updated_at"}.issubset(payload[0].keys())


def test_api_v1_density_summary_endpoint():
    response = client.get("/api/v1/traffic/density")

    assert response.status_code == 200
    payload = response.json()
    required = {"total_roads", "total_roads_monitored", "total_vehicle_count", "average_density", "average_network_density", "maximum_density", "minimum_density", "high_congestion_roads", "severe_congestion_roads", "congested_segments", "timestamp"}
    assert required.issubset(payload.keys())


def test_api_v1_road_detail_endpoint_success_and_not_found():
    success = client.get("/api/v1/traffic/road/1")
    not_found = client.get("/api/v1/traffic/road/UNKNOWN")

    assert success.status_code == 200
    payload = success.json()
    assert payload["road_id"] == "1"
    assert "history" in payload
    assert isinstance(payload["history"], list)
    assert not_found.status_code == 404


def test_api_v1_prediction_and_cors_headers():
    response = client.get("/api/v1/predict/congestion?road_id=1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["road_id"] == "1"
    assert payload["model_version"] == "ml-v2"

    cors = client.options(
        "/api/v1/traffic/live",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert cors.status_code in {200, 204}
    assert cors.headers.get("access-control-allow-origin") in {"http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"}
