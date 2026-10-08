import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


# =========================================================
# DEF-M3-009
# MALFORMED DATE TESTS
# =========================================================


def test_invalid_trends_date():

    with patch("main.road_exists", return_value=True):

        response = client.get("/analytics/trends" "?road_id=R001" "&start_date=abc")

    assert response.status_code == 422


def test_invalid_heatmap_date():

    response = client.get("/analytics/heatmap" "?start_date=abc")

    assert response.status_code == 422


def test_invalid_report_date():

    response = client.get("/analytics/reports" "?start_date=abc")

    assert response.status_code == 422


# =========================================================
# DEF-M3-011
# INVERTED DATE RANGE
# =========================================================


def test_invalid_date_range_trends():

    with patch("main.road_exists", return_value=True):

        response = client.get(
            "/analytics/trends" "?road_id=R001" "&start_date=2026-08-23" "&end_date=2026-07-27"
        )

    assert response.status_code == 400


def test_invalid_date_range_heatmap():

    response = client.get("/analytics/heatmap" "?start_date=2026-08-23" "&end_date=2026-07-27")

    assert response.status_code == 400


def test_invalid_date_range_report():

    response = client.get("/analytics/reports" "?start_date=2026-08-23" "&end_date=2026-07-27")

    assert response.status_code == 400


# =========================================================
# DEF-M3-011
# UNKNOWN ROAD
# =========================================================


def test_unknown_trends_road():

    with patch("main.road_exists", return_value=False):

        response = client.get("/analytics/trends" "?road_id=R999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Road 'R999' not found"


def test_unknown_report_road():

    with patch("main.road_exists", return_value=False):

        response = client.get("/analytics/reports" "?road_id=R999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Road 'R999' not found"


# =========================================================
# DEF-M3-014
# CORS
# =========================================================


def test_cors_header():

    response = client.options(
        "/analytics/heatmap",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200

    assert response.headers.get("access-control-allow-origin") == "*"


# =========================================================
# DEF-M3-010
# REPORT USES IST
# =========================================================


def test_report_uses_ist_date_filter():

    fake_rows = []

    captured = {}

    class FakeCursor:

        def execute(self, query, params):

            captured["query"] = query
            captured["params"] = params

        def fetchall(self):

            return fake_rows

    class FakeConnection:

        def cursor(self):

            return FakeCursor()

        def close(self):

            pass

    with patch("report_service.get_postgres_connection", return_value=FakeConnection()):

        from report_service import generate_historical_report

        generate_historical_report(
            road_id="R001", start_date="2026-07-27", end_date="2026-08-23", limit=100
        )

    assert "Asia/Kolkata" in captured["query"]

    assert "::date >= %s::date" in captured["query"]

    assert "::date <= %s::date" in captured["query"]
