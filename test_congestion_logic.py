"""
TrafficVision AI — Unit Tests for congestion_logic.py (Day 6)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Run:
    pytest test_congestion_logic.py -v
"""

import pytest
from congestion_logic import calculate_congestion_level, calculate_avg_speed


class TestCalculateCongestionLevel:
    """Tests for the density -> congestion category threshold rule."""

    def test_low_congestion(self):
        assert calculate_congestion_level(0) == "LOW"
        assert calculate_congestion_level(15) == "LOW"
        assert calculate_congestion_level(29.99) == "LOW"

    def test_moderate_congestion(self):
        assert calculate_congestion_level(30) == "MODERATE"
        assert calculate_congestion_level(45) == "MODERATE"
        assert calculate_congestion_level(59.99) == "MODERATE"

    def test_high_congestion(self):
        assert calculate_congestion_level(60) == "HIGH"
        assert calculate_congestion_level(70) == "HIGH"
        assert calculate_congestion_level(84.99) == "HIGH"

    def test_severe_congestion(self):
        assert calculate_congestion_level(85) == "SEVERE"
        assert calculate_congestion_level(100) == "SEVERE"

    def test_boundary_values_exactly(self):
        """
        These are the exact threshold edges — the most important cases to
        test, since off-by-one errors in threshold logic are a common bug.
        """
        assert calculate_congestion_level(29.99) == "LOW"
        assert calculate_congestion_level(30.0) == "MODERATE"
        assert calculate_congestion_level(59.99) == "MODERATE"
        assert calculate_congestion_level(60.0) == "HIGH"
        assert calculate_congestion_level(84.99) == "HIGH"
        assert calculate_congestion_level(85.0) == "SEVERE"

    def test_negative_density_does_not_crash(self):
        """
        Density should never realistically be negative, but the function
        shouldn't crash if it happens (e.g. due to a bad sensor reading).
        """
        assert calculate_congestion_level(-5) == "LOW"


class TestCalculateAvgSpeed:
    """Tests for the simulated speed-from-density relationship."""

    def test_speed_never_goes_below_minimum_floor(self):
        """Even at max density, speed should never drop below 5 km/h."""
        for _ in range(20):  # run several times since there's randomness involved
            speed = calculate_avg_speed(100)
            assert speed >= 5

    def test_speed_decreases_as_density_increases_on_average(self):
        """
        Because there's random noise involved, we can't check exact
        values — but average speed at low density should clearly be
        higher than average speed at high density across many samples.
        """
        low_density_speeds = [calculate_avg_speed(10) for _ in range(50)]
        high_density_speeds = [calculate_avg_speed(90) for _ in range(50)]

        avg_low = sum(low_density_speeds) / len(low_density_speeds)
        avg_high = sum(high_density_speeds) / len(high_density_speeds)

        assert avg_low > avg_high

    def test_returns_a_number(self):
        result = calculate_avg_speed(50)
        assert isinstance(result, (int, float))
