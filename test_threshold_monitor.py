"""
TrafficVision AI — Unit Tests for threshold_monitor.py (Milestone 3, Day 6)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Run:
    pytest test_threshold_monitor.py -v
"""

from datetime import datetime, timedelta
import pytest

import threshold_monitor


class TestCooldownLogic:
    """
    These tests directly manipulate threshold_monitor's module-level
    _last_alert_time dict to control exact timing — the same approach
    used to manually verify this logic on Day 2, now formalized as
    repeatable automated tests.
    """

    def setup_method(self):
        """Reset the cooldown state before each test, so tests don't interfere with each other."""
        threshold_monitor._last_alert_time = {}

    def test_road_never_alerted_is_not_in_cooldown(self):
        assert threshold_monitor.is_in_cooldown(999) is False

    def test_road_alerted_just_now_is_in_cooldown(self):
        threshold_monitor._last_alert_time[1] = datetime.now()
        assert threshold_monitor.is_in_cooldown(1) is True

    def test_cooldown_expires_after_configured_duration(self):
        past_time = datetime.now() - timedelta(seconds=threshold_monitor.COOLDOWN_SECONDS + 1)
        threshold_monitor._last_alert_time[2] = past_time
        assert threshold_monitor.is_in_cooldown(2) is False

    def test_still_in_cooldown_before_duration_elapses(self):
        recent_time = datetime.now() - timedelta(seconds=threshold_monitor.COOLDOWN_SECONDS / 2)
        threshold_monitor._last_alert_time[3] = recent_time
        assert threshold_monitor.is_in_cooldown(3) is True

    def test_different_roads_have_independent_cooldowns(self):
        """
        A cooldown on one road should never affect another — this is
        the kind of bug that could slip in if cooldown state were
        accidentally shared instead of keyed per-road.
        """
        threshold_monitor._last_alert_time[4] = datetime.now()  # road 4 in cooldown
        assert threshold_monitor.is_in_cooldown(4) is True
        assert threshold_monitor.is_in_cooldown(5) is False  # road 5 unaffected
