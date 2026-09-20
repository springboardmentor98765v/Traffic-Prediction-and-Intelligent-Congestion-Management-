"""
TrafficVision AI — Unit Tests for generate_historical_data.py (Milestone 2, Day 6)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Run:
    pytest test_generate_historical_data.py -v
"""

from datetime import datetime
import pytest

from generate_historical_data import get_density_for_timestamp


class TestGetDensityForTimestamp:
    """
    Tests the weekday/weekend and hour-of-day pattern logic that makes
    the historical dataset genuinely learnable, not just random noise.
    """

    def test_weekday_rush_hour_exceeds_weekend_rush_hour(self):
        """This is the core Day 2 claim — verify it holds across many samples."""
        monday_8am = datetime(2026, 9, 21, 8, 0)   # Monday
        saturday_8am = datetime(2026, 9, 26, 8, 0)  # Saturday

        weekday_samples = [get_density_for_timestamp(monday_8am) for _ in range(200)]
        weekend_samples = [get_density_for_timestamp(saturday_8am) for _ in range(200)]

        avg_weekday = sum(weekday_samples) / len(weekday_samples)
        avg_weekend = sum(weekend_samples) / len(weekend_samples)

        assert avg_weekday > avg_weekend

    def test_rush_hour_exceeds_late_night(self):
        monday_8am = datetime(2026, 9, 21, 8, 0)
        monday_3am = datetime(2026, 9, 21, 3, 0)

        rush_samples = [get_density_for_timestamp(monday_8am) for _ in range(200)]
        night_samples = [get_density_for_timestamp(monday_3am) for _ in range(200)]

        avg_rush = sum(rush_samples) / len(rush_samples)
        avg_night = sum(night_samples) / len(night_samples)

        assert avg_rush > avg_night

    def test_density_always_within_valid_range(self):
        """Density should never go below 0 or above 100, regardless of inputs."""
        test_times = [
            datetime(2026, 9, 21, h, 0) for h in range(24)
        ]
        for ts in test_times:
            for _ in range(20):
                density = get_density_for_timestamp(ts)
                assert 0 <= density <= 100

    def test_returns_a_float(self):
        result = get_density_for_timestamp(datetime(2026, 9, 21, 12, 0))
        assert isinstance(result, float)

    def test_weekend_evening_shoulder_hour_still_lower_than_weekday(self):
        """
        Checks a second weekday/weekend pair (not just the 8am case) to
        make sure the weekend scaling applies consistently, not just at
        one specific hour that might have been hardcoded by accident.
        """
        monday_6pm = datetime(2026, 9, 21, 18, 0)
        saturday_6pm = datetime(2026, 9, 26, 18, 0)

        weekday_samples = [get_density_for_timestamp(monday_6pm) for _ in range(200)]
        weekend_samples = [get_density_for_timestamp(saturday_6pm) for _ in range(200)]

        avg_weekday = sum(weekday_samples) / len(weekday_samples)
        avg_weekend = sum(weekend_samples) / len(weekend_samples)

        assert avg_weekday > avg_weekend
