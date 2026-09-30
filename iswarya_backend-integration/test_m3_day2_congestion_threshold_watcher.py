from unittest.mock import Mock

from src.m3_day2_congestion_watcher import (
    CongestionThresholdWatcher
)


def test_high_congestion_triggers_alert():
    watcher = CongestionThresholdWatcher()

    watcher.send_alert = Mock(
        return_value={
            "alert_id": "A001",
            "status": "created"
        }
    )

    reading = {
        "road_id": "R001",
        "vehicle_count": 82,
        "density": 16.4,
        "congestion_level": "High",
        "avg_speed_kmph": 22.5,
        "updated_at": (
            "2026-08-31T09:00:00+05:30"
        )
    }

    result = watcher.check_reading(
        reading
    )

    assert result["threshold_breached"] is True
    assert result["alert_triggered"] is True

    watcher.send_alert.assert_called_once()


def test_severe_congestion_maps_to_critical():
    watcher = CongestionThresholdWatcher()

    reading = {
        "road_id": "R002",
        "vehicle_count": 120,
        "density": 24.5,
        "congestion_level": "Severe",
        "avg_speed_kmph": 12.0,
        "updated_at": (
            "2026-08-31T10:00:00+05:30"
        )
    }

    payload = watcher.build_alert_payload(
        reading
    )

    assert payload["severity"] == "Critical"


def test_alert_sends_producer_key():
    watcher = CongestionThresholdWatcher(
        alert_api_url="http://alert-service/api/v1/alerts/",
        alert_service_key="test-secret"
    )

    watcher.send_alert = Mock(
        return_value={
            "alert_id": "A003",
            "status": "created"
        }
    )

    payload = {
        "type": "congestion",
        "severity": "High",
        "road_id": "R001",
        "message": "High congestion threshold breached."
    }

    watcher.send_alert(payload)

    assert watcher.alert_service_key == "test-secret"

    headers = watcher._build_headers()

    assert headers[
        "X-Alert-Service-Key"
    ] == "test-secret"


def test_low_congestion_does_not_trigger_alert():
    watcher = CongestionThresholdWatcher()

    watcher.send_alert = Mock()

    reading = {
        "road_id": "R003",
        "vehicle_count": 25,
        "density": 5.2,
        "congestion_level": "Low",
        "avg_speed_kmph": 45.0,
        "updated_at": (
            "2026-08-31T11:00:00+05:30"
        )
    }

    result = watcher.check_reading(
        reading
    )

    assert result["threshold_breached"] is False
    assert result["alert_triggered"] is False

    watcher.send_alert.assert_not_called()


def test_medium_congestion_does_not_trigger_alert():
    watcher = CongestionThresholdWatcher()

    watcher.send_alert = Mock()

    reading = {
        "road_id": "R004",
        "vehicle_count": 55,
        "density": 9.5,
        "congestion_level": "Medium",
        "avg_speed_kmph": 35.0,
        "updated_at": (
            "2026-08-31T12:00:00+05:30"
        )
    }

    result = watcher.check_reading(
        reading
    )

    assert result["threshold_breached"] is False
    assert result["alert_triggered"] is False

    watcher.send_alert.assert_not_called()


def test_duplicate_alert_is_prevented():
    watcher = CongestionThresholdWatcher()

    watcher.send_alert = Mock(
        return_value={
            "alert_id": "A004",
            "status": "created"
        }
    )

    reading = {
        "road_id": "R005",
        "vehicle_count": 100,
        "density": 20.0,
        "congestion_level": "High",
        "avg_speed_kmph": 18.0,
        "updated_at": (
            "2026-08-31T13:00:00+05:30"
        )
    }

    first_result = watcher.check_reading(
        reading
    )

    second_result = watcher.check_reading(
        reading
    )

    assert first_result["alert_triggered"] is True

    assert second_result[
        "alert_triggered"
    ] is False

    assert second_result[
        "reason"
    ] == "alert_already_active"

    assert (
        watcher.send_alert.call_count == 1
    )


def test_alert_state_resets_after_congestion_drops():
    watcher = CongestionThresholdWatcher()

    watcher.send_alert = Mock(
        return_value={
            "alert_id": "A005",
            "status": "created"
        }
    )

    high_reading = {
        "road_id": "R006",
        "vehicle_count": 90,
        "density": 18.0,
        "congestion_level": "High",
        "avg_speed_kmph": 20.0,
        "updated_at": (
            "2026-08-31T14:00:00+05:30"
        )
    }

    low_reading = {
        "road_id": "R006",
        "vehicle_count": 25,
        "density": 5.0,
        "congestion_level": "Low",
        "avg_speed_kmph": 45.0,
        "updated_at": (
            "2026-08-31T15:00:00+05:30"
        )
    }

    first_result = watcher.check_reading(
        high_reading
    )

    watcher.check_reading(
        low_reading
    )

    third_result = watcher.check_reading(
        high_reading
    )

    assert first_result[
        "alert_triggered"
    ] is True

    assert third_result[
        "alert_triggered"
    ] is True

    assert watcher.send_alert.call_count == 2