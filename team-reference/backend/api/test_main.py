from datetime import datetime
from pathlib import Path
import secrets

import httpx
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
import api.main as main_module
from api import state_store

client = TestClient(app)


def admin_headers(tmp_path: Path, monkeypatch):
    users_path = tmp_path / "users.json"
    monkeypatch.setattr(main_module, "AUTH_DATA_PATH", users_path)
    main_module._write_users({"admin@example.test": {"name": "Test Admin", "role": "ADMIN", "password_hash": "unused"}})
    token = main_module._encode_token("admin@example.test", "ADMIN", 3600, "access", "test-access")
    return {"Authorization": f"Bearer {token}"}


def test_state_store_persists_session_and_alert_rows(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(state_store, "STATE_DB_PATH", tmp_path / "state.sqlite3")

    with state_store.open_state() as connection:
        connection.execute(
            "INSERT INTO auth_sessions (refresh_jti, email, role, expires_at) VALUES (?, ?, ?, ?)",
            ("refresh-1", "user@example.com", "USER", 2_000_000_000),
        )
        connection.execute(
            "INSERT INTO alerts (alert_id, road_id, type, severity, title, message, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("alert-1", "R001", "hazard", "high", "Road hazard", "Reported hazard", "2026-10-01T00:00:00+00:00"),
        )

    with state_store.open_state() as connection:
        assert connection.execute("SELECT email FROM auth_sessions WHERE refresh_jti = ?", ("refresh-1",)).fetchone()["email"] == "user@example.com"
        assert connection.execute("SELECT message FROM alerts WHERE alert_id = ?", ("alert-1",)).fetchone()["message"] == "Reported hazard"


def test_auth_register_login_and_role_protection(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(main_module, "AUTH_DATA_PATH", tmp_path / "users.json")
    monkeypatch.setattr(state_store, "STATE_DB_PATH", tmp_path / "state.sqlite3")
    test_password = secrets.token_urlsafe(18)
    captcha = client.get("/api/v1/auth/captcha").json()
    registration = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test-auth@example.com",
        "password": test_password,
        "role": "ADMIN",
        "challenge_id": captcha["challenge_id"],
        "captcha_response": main_module.CAPTCHA_CHALLENGES[captcha["challenge_id"]][0],
    })

    assert registration.status_code == 201
    assert registration.json()["role"] == "USER"
    assert test_password not in (tmp_path / "users.json").read_text()

    login_captcha = client.get("/api/v1/auth/captcha").json()
    code = main_module.CAPTCHA_CHALLENGES[login_captcha["challenge_id"]][0]
    login = client.post("/api/v1/auth/login", json={
        "email": "test-auth@example.com",
        "password": test_password,
        "challenge_id": login_captcha["challenge_id"],
        "captcha_response": code,
    })

    assert login.status_code == 200
    assert login.json()["role"] == "USER"
    profile = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert profile.status_code == 200
    assert profile.json()["role"] == "USER"

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert refresh.status_code == 200
    assert refresh.json()["access_token"] != login.json()["access_token"]
    replay = client.post("/api/v1/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert replay.status_code == 401

    logout = client.post("/api/v1/auth/logout", json={"refresh_token": refresh.json()["refresh_token"]})
    assert logout.status_code == 200
    revoked = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh.json()["refresh_token"]})
    assert revoked.status_code == 401


def test_default_admin_login_uses_configured_credential(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(main_module, "AUTH_DATA_PATH", tmp_path / "users.json")
    admin_password = secrets.token_urlsafe(24)
    monkeypatch.setattr(main_module, "DEFAULT_ADMIN_PASSWORD", admin_password)
    captcha = client.get("/api/v1/auth/captcha").json()
    login = client.post("/api/v1/auth/login", json={
        "email": "admin.gmail.com",
        "password": admin_password,
        "challenge_id": captcha["challenge_id"],
        "captcha_response": main_module.CAPTCHA_CHALLENGES[captcha["challenge_id"]][0],
    })

    assert login.status_code == 200
    assert login.json()["role"] == "ADMIN"
    assert login.json()["name"] == "System Administrator"


def test_captcha_endpoint_and_local_development_cors():
    response = client.get("/api/v1/auth/captcha")

    assert response.status_code == 200
    payload = response.json()
    assert payload["challenge_id"]
    assert payload["image"].startswith("data:image/svg+xml;base64,")

    cors = client.options(
        "/api/v1/auth/captcha",
        headers={
            "Origin": "http://127.0.0.1:5501",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert cors.status_code in {200, 204}
    assert cors.headers.get("access-control-allow-origin") == "http://127.0.0.1:5501"
    report = client.get(
        "/api/v1/analytics/reports?range=day&format=csv",
        headers={"Origin": "http://127.0.0.1:5501"},
    )
    assert report.status_code == 200
    assert "content-disposition" in report.headers.get("access-control-expose-headers", "").lower()


def test_prediction_uses_latest_data_engineering_record():
    result = predict_congestion_api("1")

    assert result.road_id == "R001"
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

    assert result.road_id == "R001"
    assert result.predicted_level in {"LOW", "MEDIUM", "HIGH", "SEVERE"}
    assert result.density == 0.4


def test_unknown_road_returns_not_found():
    with pytest.raises(HTTPException) as error:
        predict_congestion_api("UNKNOWN")

    assert error.value.status_code == 404


def test_peak_hours_and_delay_are_model_backed():
    peak_hours = predict_peak_hours("1")
    delay = predict_delay("1", distance_km=2)

    assert peak_hours.road_id == "R001"
    assert len(peak_hours.peak_windows) == 3
    assert len(peak_hours.hourly_data) == 24
    assert peak_hours.data_source == "local-processed-csv"
    assert delay.predicted_level in {"LOW", "MEDIUM", "HIGH", "SEVERE"}
    assert delay.model_version == "ml-v2"
    assert delay.road_id == "R001"
    assert delay.estimated_delay_minutes >= 0


def test_route_ranking_prefers_less_congested_route():
    ranked = rank_routes(RouteRankingRequest(routes=[
        {"route_id": "first", "distance_km": 2, "roads": ["1"]},
        {"route_id": "second", "distance_km": 2, "roads": ["2"]},
    ]))

    assert len(ranked) == 2
    assert ranked[0].score >= ranked[1].score
    assert ranked[0].is_recommended is True
    assert ranked[0].estimated_travel_time_minutes > 0
    assert ranked[0].road_predictions[0]["confidence"] > 0


def test_osrm_route_geometry_is_real_converted_and_persisted(tmp_path, monkeypatch):
    monkeypatch.setattr(state_store, "STATE_DB_PATH", tmp_path / "routes.sqlite3")

    async def fake_osrm(_origin, _destination, alternatives):
        route_list = [
            {"distance": 5000, "duration": 600, "geometry": {"coordinates": [[91.7, 26.1], [91.8, 26.2]]}},
            {"distance": 6000, "duration": 720, "geometry": {"coordinates": [[91.7, 26.1], [91.75, 26.15], [91.8, 26.2]]}},
        ]
        return {"code": "Ok", "routes": route_list if alternatives else route_list[:1]}

    monkeypatch.setattr(main_module, "_fetch_osrm_routes", fake_osrm)
    optimized = client.get("/api/v1/route/optimize?origin=26.1,91.7&destination=26.2,91.8")

    assert optimized.status_code == 200
    route = optimized.json()
    assert route["source"] == "OSRM"
    assert route["path"] == [[26.1, 91.7], [26.2, 91.8]]
    assert route["distance_km"] == 5.0
    assert route["traffic_impact_available"] is False
    assert client.get(f"/api/v1/route/travel-time?route_id={route['route_id']}").json()["estimated_minutes"] == 10

    alternates = client.get("/api/v1/route/alternate?origin=26.1,91.7&destination=26.2,91.8")
    assert alternates.status_code == 200
    assert len(alternates.json()) == 2
    assert alternates.json()[0]["is_recommended"] is True


def test_osrm_route_rejects_invalid_coordinates():
    response = client.get("/api/v1/route/optimize?origin=999,91&destination=26.2,91.8")

    assert response.status_code == 422


def test_osrm_route_reports_timeout_and_provider_errors(monkeypatch):
    async def timeout_case(_origin, _destination, alternatives):
        raise httpx.TimeoutException("OSRM timed out")

    monkeypatch.setattr(main_module, "_fetch_osrm_routes", timeout_case)
    timeout_response = client.get("/api/v1/route/alternate?origin=13.0827,80.2707&destination=13.0569,80.2425")
    assert timeout_response.status_code == 503
    assert "unavailable" in timeout_response.json()["detail"].lower()

    async def provider_error_case(_origin, _destination, alternatives):
        raise httpx.HTTPStatusError("provider rejected request", request=None, response=None)

    monkeypatch.setattr(main_module, "_fetch_osrm_routes", provider_error_case)
    error_response = client.get("/api/v1/route/alternate?origin=13.0827,80.2707&destination=13.0569,80.2425")
    assert error_response.status_code == 503
    assert "unavailable" in error_response.json()["detail"].lower()


def test_osrm_route_rejects_malformed_geometry():
    malformed = {
        "code": "Ok",
        "routes": [{
            "distance": 5000,
            "duration": 600,
            "geometry": {"coordinates": [[80.27, 13.08, 99], [80.25, 13.05, 100]]},
        }],
    }

    with pytest.raises(HTTPException) as exc:
        main_module._cache_osrm_route(malformed["routes"][0])

    assert exc.value.status_code == 502


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


def test_source_traffic_analytics_contracts_use_csv_records():
    history = client.get("/api/v1/traffic/history?road_id=1&limit=2")
    aggregate = client.get("/api/v1/traffic/aggregate?road_id=R001&granularity=hour")
    daily = client.get("/api/v1/analytics/trends?road_id=R001&range=day")
    weekly = client.get("/api/v1/analytics/trends?road_id=1&range=week")
    heatmap = client.get("/api/v1/analytics/heatmap?range=week")
    report_json = client.get("/api/v1/analytics/reports?range=week&format=json")
    report_csv = client.get("/api/v1/analytics/reports?range=day&format=csv")
    condition = client.get("/api/v1/route/conditions?road_id=1")

    assert all(response.status_code == 200 for response in [history, aggregate, daily, weekly, heatmap, report_json, report_csv, condition])
    assert len(history.json()) == 2 and history.json()[0]["road_id"] == "R001"
    assert aggregate.json() and aggregate.json()[0]["sample_count"] > 0
    assert len(daily.json()["points"]) <= 24 and daily.json()["points"]
    assert weekly.json()["points"]
    assert len(heatmap.json()["roads"]) == 5
    assert all(len(row) == 24 for row in heatmap.json()["values"])
    assert all(value is None or 0 <= value <= 1 for row in heatmap.json()["values"] for value in row)
    assert report_json.json()["record_count"] > 0
    assert report_csv.headers["content-type"].startswith("text/csv")
    assert condition.json()["condition_source"] == "traffic-csv-congestion-only"
    assert "no closure" in condition.json()["notes"]


def test_api_v1_anomalies_are_model_backed_and_bounded():
    response = client.get("/api/v1/ai/anomalies?limit=3&window_rows=20")

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_version"] == "ml-v2"
    assert payload["data_source"] == "local-processed-csv"
    assert 0 < payload["evaluated_rows"] <= 20
    assert len(payload["anomalies"]) <= 3
    assert "do not establish that an accident occurred" in payload["interpretation"]
    assert all(0 <= item["anomaly_score"] <= 1 for item in payload["anomalies"])


def test_persistent_alert_create_active_and_mark_read(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(state_store, "STATE_DB_PATH", tmp_path / "alerts.sqlite3")
    headers = admin_headers(tmp_path, monkeypatch)
    created = client.post("/api/v1/alerts", json={
        "type": "hazard",
        "severity": "high",
        "road_id": "1",
        "message": "Test-only road hazard",
    }, headers=headers)

    assert created.status_code == 201
    alert_id = created.json()["alert_id"]
    active = client.get("/api/v1/alerts/active")
    assert any(alert["alert_id"] == alert_id for alert in active.json())

    marked = client.post(f"/api/v1/alerts/{alert_id}/read")
    assert marked.status_code == 200
    assert marked.json()["read"] is True
    assert all(alert["alert_id"] != alert_id for alert in client.get("/api/v1/alerts/active").json())
    assert any(alert["alert_id"] == alert_id for alert in client.get("/api/v1/alerts").json())


def test_anomaly_sync_is_idempotent(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(state_store, "STATE_DB_PATH", tmp_path / "alerts.sqlite3")
    headers = admin_headers(tmp_path, monkeypatch)
    monkeypatch.setattr(main_module, "_build_anomalies", lambda **_: {
        "data_source": "local-processed-csv",
        "anomalies": [{
            "road_id": "R001",
            "timestamp": "2026-09-18T23:55:00",
            "observed_congestion": "HIGH",
            "predicted_congestion": "LOW",
            "severity": "high",
            "anomaly_score": 0.667,
            "reason": "Test mismatch",
        }],
    })

    first = client.post("/api/v1/alerts/sync-ai-anomalies?minimum_score=0.3", headers=headers)
    second = client.post("/api/v1/alerts/sync-ai-anomalies?minimum_score=0.3", headers=headers)

    assert first.status_code == second.status_code == 200
    assert first.json()["alerts_created"] == 1
    assert second.json()["alerts_created"] == 0
    assert second.json()["alerts_skipped"] == 1


def test_public_users_cannot_create_or_sync_alerts(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(main_module, "AUTH_DATA_PATH", tmp_path / "users.json")
    main_module._write_users({"public@example.test": {"name": "Public", "role": "USER", "password_hash": "unused"}})
    token = main_module._encode_token("public@example.test", "USER", 3600, "access", "public-access")
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post("/api/v1/alerts", json={"type": "hazard", "severity": "high", "road_id": "R001", "message": "Attempt"}, headers=headers)
    sync = client.post("/api/v1/alerts/sync-ai-anomalies", headers=headers)

    assert create.status_code == 403
    assert sync.status_code == 403


def test_api_v1_road_detail_endpoint_success_and_not_found():
    success = client.get("/api/v1/traffic/road/1")
    not_found = client.get("/api/v1/traffic/road/UNKNOWN")

    assert success.status_code == 200
    payload = success.json()
    assert payload["road_id"] == "R001"
    assert "history" in payload
    assert isinstance(payload["history"], list)
    assert not_found.status_code == 404


def test_api_v1_prediction_and_cors_headers():
    response = client.get("/api/v1/predict/congestion?road_id=1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["road_id"] == "R001"
    assert payload["model_version"] == "ml-v2"
    traffic = client.get("/api/v1/traffic/road/1").json()
    assert payload["vehicle_count"] == traffic["vehicle_count"]
    assert payload["average_speed"] == traffic["avg_speed_kmph"]
    assert payload["density"] == traffic["density"]
    assert set(payload["factors"]) == {"vehicle_count", "average_speed", "density"}

    cors = client.options(
        "/api/v1/traffic/live",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert cors.status_code in {200, 204}
    assert cors.headers.get("access-control-allow-origin") in {"http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"}


def test_health_reports_traffic_source_and_model():
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["traffic_records"] > 0
    assert payload["roads"] == ["R001", "R002", "R003", "R004", "R005"]
    assert payload["model_version"] == "ml-v2"


def test_model_accuracy_endpoint():
    for path in ["/model/accuracy", "/api/v1/model/accuracy"]:
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert "model_version" in payload
        assert "accuracy" in payload
        assert "macro_precision" in payload
        assert "macro_recall" in payload
        assert "macro_f1" in payload
        assert "weighted_f1" in payload
        assert payload["evaluation_valid"] is True
        assert "chronological holdout" in payload["evaluation_note"]
        assert 0.0 <= payload["accuracy"] <= 1.0
        assert 0.0 <= payload["macro_f1"] <= 1.0


def test_model_metrics_endpoint():
    for path in ["/model/metrics", "/api/v1/model/metrics"]:
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert payload["model_version"] == "ml-v2"
        assert 0.0 <= payload["accuracy"] <= 1.0
        assert 0.0 <= payload["macro_f1"] <= 1.0
        assert payload["training_rows"] > 0
        assert payload["test_rows"] > 0
        assert set(payload["classes"]) == {"HIGH", "LOW", "MEDIUM", "SEVERE"}
        assert "per_class" in payload
        assert "confusion_matrix" in payload
        assert payload["leakage_checks"]["train_test_timestamp_overlap"] is False
        assert payload["leakage_checks"]["preprocessing_fit_on_training_rows_only"] is True
        assert payload["artifact_metric_cross_check"]["recomputed_accuracy_matches"] is True


def test_source_model_info_aliases_and_detailed_health():
    info = client.get("/api/v1/predict/model-info")
    metrics = client.get("/api/v1/predict/model-metrics")
    health = client.get("/health/detailed")

    assert info.status_code == metrics.status_code == health.status_code == 200
    assert info.json()["model_version"] == "ml-v2"
    assert info.json()["scikit_learn_version"] == "1.9.1"
    assert info.json()["evaluation"]["test_rows"] == 8065
    assert metrics.json()["leakage_checks"]["train_test_timestamp_overlap"] is False
    assert set(health.json()["dependencies"]) == {"traffic_data", "model", "state_store"}
