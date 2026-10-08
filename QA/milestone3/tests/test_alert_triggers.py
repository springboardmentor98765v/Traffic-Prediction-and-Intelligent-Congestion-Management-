"""TC-AL-01..08 — alert trigger correctness (unit, no network).

Covers the two alert producers that feed the Alert Service:
`m3_day2_congestion_watcher.CongestionThresholdWatcher` (congestion alerts) and
`anomaly_detector.AnomalyDetector` (accident / possible_incident alerts).
"""

import pytest

from m3_day2_congestion_watcher import CongestionThresholdWatcher


def reading(level, road_id="R001", **extra):
    base = {
        "road_id": road_id,
        "vehicle_count": 82,
        "density": 16.4,
        "congestion_level": level,
        "updated_at": "2026-09-22T09:00:00+05:30",
        "avg_speed_kmph": 22.5,
    }
    base.update(extra)
    return base


@pytest.fixture
def watcher(monkeypatch):
    w = CongestionThresholdWatcher(alert_api_url="http://alert-service.invalid/api/v1/alerts/")
    w.sent = []

    def fake_send(payload):
        w.sent.append(payload)
        return {"status": "created", "alert_id": len(w.sent)}

    monkeypatch.setattr(w, "send_alert", fake_send)
    return w


@pytest.mark.parametrize("level", ["High", "Severe"])
def test_tc_al_01_high_or_severe_triggers_alert(watcher, level):
    result = watcher.check_reading(reading(level))
    assert result["threshold_breached"] is True
    assert result["alert_triggered"] is True
    assert len(watcher.sent) == 1


@pytest.mark.parametrize("level", ["Low", "Medium"])
def test_tc_al_02_low_or_medium_does_not_trigger(watcher, level):
    result = watcher.check_reading(reading(level))
    assert result["alert_triggered"] is False
    assert watcher.sent == []


def test_tc_al_03_payload_matches_frozen_alert_contract(watcher):
    watcher.check_reading(reading("High", road_id="R002"))
    assert watcher.sent == [
        {
            "type": "congestion",
            "severity": "High",
            "road_id": "R002",
            "message": "High congestion threshold breached on road R002.",
        }
    ]


def test_tc_al_04_repeated_breach_is_deduplicated(watcher):
    watcher.check_reading(reading("High"))
    second = watcher.check_reading(reading("Severe"))
    assert second["alert_triggered"] is False
    assert second["reason"] == "alert_already_active"
    assert len(watcher.sent) == 1


def test_tc_al_05_alert_rearms_after_congestion_clears(watcher):
    watcher.check_reading(reading("High"))
    watcher.check_reading(reading("Low"))
    again = watcher.check_reading(reading("High"))
    assert again["alert_triggered"] is True
    assert len(watcher.sent) == 2


def test_tc_al_06_failed_delivery_is_retried_on_next_reading(monkeypatch):
    w = CongestionThresholdWatcher(alert_api_url="http://alert-service.invalid/")
    responses = iter([{"status": "failed", "message": "timeout"}, {"status": "created"}])
    monkeypatch.setattr(w, "send_alert", lambda payload: next(responses))

    first = w.check_reading(reading("High"))
    second = w.check_reading(reading("High"))
    assert first["alert_triggered"] is False
    assert second["alert_triggered"] is True


def test_tc_al_07_unconfigured_alert_url_reports_pending():
    w = CongestionThresholdWatcher(alert_api_url=None)
    w.alert_api_url = ""
    assert w.send_alert({"type": "congestion"})["status"] == "pending"


def test_tc_al_07b_accepts_m2_field_aliases(watcher):
    r = reading("High", traffic_density=20.0, timestamp="2026-09-22T09:00:00")
    del r["density"], r["updated_at"]
    normalized = watcher.normalize_live_reading(r)
    assert normalized["traffic_density"] == 20.0
    assert normalized["timestamp"] == "2026-09-22T09:00:00"


class TestAnomalyDetector:
    """TC-AL-08 — anomaly classification that drives accident alerts."""

    @pytest.fixture(scope="class")
    def detector(self):
        from anomaly_detector import AnomalyDetector

        return AnomalyDetector()

    # Baseline R001, Tue 08:00: ~91 vehicles, ~27 km/h, density ~18.
    TS = "2026-09-22T08:00:00"

    def test_tc_al_08a_baseline_like_traffic_is_normal(self, detector):
        result = detector.analyze("R001", self.TS, 91, 27.0, 18.3)
        assert result["anomaly_class"] == "normal"

    def test_tc_al_08b_crash_signature_is_possible_incident(self, detector):
        result = detector.analyze("R001", self.TS, 200, 3.0, 60.0)
        assert result["anomaly_class"] == "possible_incident"

    def test_tc_al_08c_unknown_road_has_no_baseline(self, detector):
        result = detector.analyze("R999", self.TS, 50, 30.0, 10.0)
        assert result["anomaly_class"] == "unknown"
