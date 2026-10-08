import sys

from pathlib import Path

from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "src")
)


from fastapi.testclient import TestClient

import main

from report_service import (
    generate_historical_report
)


# =========================================================
# REPORT CSV
# =========================================================

def test_report_csv_generation():

    fake_rows = [
        (
            "R001",
            "S001",
            None,
            50,
            30.5,
            100,
            10.2,
            "Medium",
            17.1,
            78.4,
            "simulated_m2_day2"
        )
    ]

    class FakeCursor:

        def execute(
            self,
            query,
            params
        ):

            self.query = query
            self.params = params

        def fetchall(self):

            return fake_rows

    class FakeConnection:

        def cursor(self):

            return FakeCursor()

        def close(self):

            pass

    with patch(
        "report_service.get_postgres_connection",
        return_value=FakeConnection(),
    ):

        csv_text, count = (
            generate_historical_report(
                road_id="R001"
            )
        )

    assert count == 1

    assert (
        "road_id,sensor_id,reading_timestamp"
        in csv_text
    )

    assert (
        "R001,S001"
        in csv_text
    )

    assert (
        "Medium"
        in csv_text
    )


# =========================================================
# LIMIT VALIDATION
# =========================================================

def test_report_limit_validation():

    try:

        generate_historical_report(
            limit=0
        )

        assert False

    except ValueError as exc:

        assert "limit" in str(exc)


# =========================================================
# REPORT ENDPOINT
# =========================================================

def test_report_endpoint(
    monkeypatch
):

    expected = (
        "road_id,sensor_id\n"
        "R001,S001\n"
    )

    monkeypatch.setattr(
        main,
        "road_exists",
        lambda road_id: True
    )

    monkeypatch.setattr(
        main,
        "generate_historical_report",
        lambda **kwargs: (
            expected,
            1
        ),
    )

    client = TestClient(
        main.app
    )

    response = client.get(
        "/analytics/reports"
        "?road_id=R001"
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "content-type"
        ].startswith("text/csv")
    )

    assert (
        "attachment"
        in response.headers[
            "content-disposition"
        ]
    )

    assert (
        response.headers[
            "x-report-row-count"
        ]
        == "1"
    )

    assert (
        "R001,S001"
        in response.text
    )


# =========================================================
# INVALID LIMIT
# =========================================================

def test_report_endpoint_rejects_invalid_limit():

    client = TestClient(
        main.app
    )

    response = client.get(
        "/analytics/reports"
        "?limit=0"
    )

    assert response.status_code == 400