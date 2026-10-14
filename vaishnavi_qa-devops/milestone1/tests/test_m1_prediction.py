"""M1 AI Engine prediction stub (Intern 3), SRS section 7.3.

Two places serve GET /api/v1/predict/congestion:
  * the AI Engine service (ai-engine/app.py, port 8010) still has the M1 heuristic stub,
    which returns generated_by="heuristic-v0";
  * the gateway (port 8000) now serves the M2 trained model (model_version="model-v1").

The stub reads Intern 2's /traffic/live feed over HTTP. Here that call is pointed at the
in-process gateway, so the test checks Monitoring -> Prediction for real, without Docker.
"""

import importlib.util
import sys
import types
from pathlib import Path

import httpx
import pytest

REPO = Path(__file__).resolve().parents[3]
AI_APP = REPO / "TrafficVision-AI m3" / "TrafficVision-AI" / "ai-engine" / "app.py"


def _load_ai_engine():
    # Loaded under its own name: the backend package is also called "app".
    spec = importlib.util.spec_from_file_location("m1_ai_engine_app", AI_APP)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ai = _load_ai_engine()


class _GatewayResponse:
    def __init__(self, resp):
        self._resp = resp

    def raise_for_status(self):
        if self._resp.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=None)

    def json(self):
        return self._resp.json()


def _client_backed_by(gateway_client):
    class _AsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url):
            return _GatewayResponse(gateway_client.get("/api/v1/traffic/live"))

    return _AsyncClient


class _DownClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        raise httpx.ConnectError("traffic service down")

    async def __aexit__(self, *exc):
        return False


@pytest.fixture
def ai_client(client, monkeypatch):
    from fastapi.testclient import TestClient

    fake_httpx = types.SimpleNamespace(
        AsyncClient=_client_backed_by(client), HTTPError=httpx.HTTPError
    )
    monkeypatch.setattr(ai, "httpx", fake_httpx)
    return TestClient(ai.app)


# ---------- heuristic rule (unit) ----------


@pytest.mark.parametrize(
    "density, expected",
    [(0, "Low"), (9.99, "Low"), (10, "Medium"), (19.99, "Medium"), (20, "High"), (55, "High")],
)
def test_tc_pred_01_heuristic_thresholds(density, expected):
    level, reason = ai.predict_congestion(vehicle_count=10, density=density, avg_speed_kmph=0)
    assert level == expected and reason


# ---------- stub endpoint (integration with the live feed) ----------


def test_tc_pred_02_stub_returns_contract_fields(ai_client):
    resp = ai_client.get("/api/v1/predict/congestion", params={"road_id": "R001"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert {"road_id", "predicted_level", "confidence", "generated_by"} <= body.keys()
    assert body["road_id"] == "R001"
    assert body["generated_by"] == "heuristic-v0"
    assert 0 <= body["confidence"] <= 1


def test_tc_pred_03_stub_uses_live_density(ai_client, client):
    for row in client.get("/api/v1/traffic/live").json():
        expected, _ = ai.predict_congestion(row["vehicle_count"], row["density"], 0)
        body = ai_client.get("/api/v1/predict/congestion", params={"road_id": row["road_id"]})
        assert body.json()["predicted_level"] == expected, row


def test_tc_pred_04_stub_unknown_road_404(ai_client):
    resp = ai_client.get("/api/v1/predict/congestion", params={"road_id": "R999"})
    assert resp.status_code == 404


def test_tc_pred_05_stub_missing_road_id_422(ai_client):
    assert ai_client.get("/api/v1/predict/congestion").status_code == 422


def test_tc_pred_06_stub_returns_503_when_monitoring_down(monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setattr(
        ai, "httpx", types.SimpleNamespace(AsyncClient=_DownClient, HTTPError=httpx.HTTPError)
    )
    resp = TestClient(ai.app).get("/api/v1/predict/congestion", params={"road_id": "R001"})
    assert resp.status_code == 503


# ---------- gateway route (now backed by the M2 model) ----------


def test_tc_pred_07_gateway_predict_route_reachable(client, monkeypatch):
    """The gateway route needs road metadata from Postgres; stub just that lookup."""
    from app.routes import predict

    monkeypatch.setattr(predict, "get_road_metadata", lambda road_id: (1000.0, 5.0))
    resp = client.get("/api/v1/predict/congestion", params={"road_id": "R001"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["road_id"] == "R001"
    assert body["predicted_level"]
    assert 0 <= body["confidence"] <= 1
    assert body["model_version"] == "model-v1"


def test_tc_pred_08_gateway_predict_unknown_road_404(client):
    resp = client.get("/api/v1/predict/congestion", params={"road_id": "R999"})
    assert resp.status_code == 404
