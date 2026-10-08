from datetime import datetime

import pytest

from app.services import traffic_service


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.query = ""
        self.params = ()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, params=()):
        self.query = query
        self.params = params

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows):
        self.cursor_instance = FakeCursor(rows)
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def close(self):
        self.closed = True


def test_history_applies_road_time_window_and_limit(monkeypatch):
    connection = FakeConnection([("R001", 12, 4.5, "Low", datetime(2026, 8, 1, 1))])
    monkeypatch.setattr(traffic_service, "get_postgres_connection", lambda: connection)

    result = traffic_service.get_traffic_history(
        road_id="R001",
        start_time="2026-08-01T00:00:00",
        end_time="2026-08-01T05:00:00",
        limit=6,
    )

    query = connection.cursor_instance.query
    assert "road_id = %s" in query
    assert "reading_timestamp >= %s" in query
    assert "reading_timestamp <= %s" in query
    assert connection.cursor_instance.params == (
        "R001",
        "2026-08-01T00:00:00",
        "2026-08-01T05:00:00",
        6,
    )
    assert result[0]["road_id"] == "R001"
    assert connection.closed


def test_aggregate_applies_filters_and_requested_bucket(monkeypatch):
    connection = FakeConnection([("R001", datetime(2026, 8, 1), 4.0, 6.5, 1)])
    monkeypatch.setattr(traffic_service, "get_postgres_connection", lambda: connection)

    result = traffic_service.get_traffic_aggregate(
        road_id="R001",
        start_time="2026-08-01",
        end_time="2026-08-07",
        interval="hour",
    )

    query = connection.cursor_instance.query
    assert "date_trunc('hour'" in query
    assert "reading_timestamp >= %s" in query
    assert "reading_timestamp <= %s" in query
    assert connection.cursor_instance.params == (
        "R001",
        "2026-08-01",
        "2026-08-07",
    )
    assert result[0]["road_id"] == "R001"
    assert connection.closed


def test_history_rejects_inverted_time_window(monkeypatch):
    monkeypatch.setattr(
        traffic_service,
        "get_postgres_connection",
        lambda: pytest.fail("database should not be queried for invalid range"),
    )

    with pytest.raises(ValueError, match="start_time must not be after end_time"):
        traffic_service.get_traffic_history(
            road_id="R001",
            start_time="2026-08-20",
            end_time="2026-08-01",
        )
