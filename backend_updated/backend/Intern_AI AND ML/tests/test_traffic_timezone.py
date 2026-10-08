from datetime import datetime

from app.services.traffic_service import _format_timestamp


def test_naive_traffic_timestamp_is_serialized_with_ist_offset():
    formatted = _format_timestamp(datetime(2026, 8, 23, 23, 0, 0))
    assert formatted == "2026-08-23T23:00:00+05:30"
