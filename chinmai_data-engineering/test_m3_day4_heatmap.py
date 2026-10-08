from unittest.mock import patch

from heatmap_service import get_traffic_heatmap


def test_heatmap_returns_grid_structure():

    fake_rows = [
        (
            "R001",
            18,
            101.75,
            25.27,
            20.35,
            21.80,
            4,
            0,
            1,
            3,
            0,
        ),
        (
            "R002",
            18,
            95.50,
            27.10,
            18.40,
            20.10,
            4,
            0,
            2,
            2,
            0,
        ),
    ]

    class FakeCursor:
        def execute(self, query, params):
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
        "heatmap_service.get_postgres_connection",
        return_value=FakeConnection()
    ):
        result = get_traffic_heatmap(
            start_date="2026-07-27",
            end_date="2026-08-23",
            time_bucket="hour"
        )

    assert result["source"] == "M2 traffic_history"
    assert result["time_bucket"] == "hour"

    assert result["roads"] == ["R001", "R002"]

    assert "18" in result["time_buckets"]

    assert len(result["grid"]) == 2

    first_cell = result["grid"][0]

    assert first_cell["road_id"] == "R001"
    assert first_cell["time_bucket"] == 18
    assert first_cell["avg_density"] == 20.35
    assert first_cell["congestion_level"] == "High"


def test_invalid_time_bucket():

    try:
        get_traffic_heatmap(time_bucket="invalid")
        assert False
    except ValueError as exc:
        assert "time_bucket" in str(exc)