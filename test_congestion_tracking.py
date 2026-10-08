"""
TrafficVision AI — Unit Tests for congestion_tracking.py (Day 6)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Run:
    pytest test_congestion_tracking.py -v
"""

import pytest
from congestion_tracking import calculate_road_utilization, build_congestion_state_history


class TestCalculateRoadUtilization:

    def test_normal_utilization(self):
        # 40 vehicles, 4 lanes, default capacity 30/lane -> 40/120 = 33.33%
        assert calculate_road_utilization(40, 4) == 33.33

    def test_full_utilization_caps_at_100(self):
        # 150 vehicles, 4 lanes -> would be 125%, should cap at 100
        assert calculate_road_utilization(150, 4) == 100.0

    def test_zero_vehicles(self):
        assert calculate_road_utilization(0, 4) == 0.0

    def test_zero_lanes_does_not_crash(self):
        """
        This is a defect QA could realistically catch — dividing by
        zero lanes would crash the API. The function should handle
        this gracefully instead of throwing a ZeroDivisionError.
        """
        assert calculate_road_utilization(50, 0) == 0.0

    def test_custom_capacity_per_lane(self):
        # 60 vehicles, 2 lanes, capacity 20/lane -> 60/40 = 150% -> capped at 100
        assert calculate_road_utilization(60, 2, capacity_per_lane=20) == 100.0


class TestBuildCongestionStateHistory:

    def test_empty_readings_returns_empty_list(self):
        assert build_congestion_state_history([]) == []

    def test_single_reading_returns_one_segment(self):
        readings = [{"congestion_level": "LOW", "recorded_at": "10:00"}]
        result = build_congestion_state_history(readings)
        assert len(result) == 1
        assert result[0]["congestion_level"] == "LOW"
        assert result[0]["from"] == "10:00"
        assert result[0]["to"] == "10:00"

    def test_all_same_level_collapses_to_one_segment(self):
        readings = [
            {"congestion_level": "LOW", "recorded_at": "10:00"},
            {"congestion_level": "LOW", "recorded_at": "10:05"},
            {"congestion_level": "LOW", "recorded_at": "10:10"},
        ]
        result = build_congestion_state_history(readings)
        assert len(result) == 1
        assert result[0]["from"] == "10:00"
        assert result[0]["to"] == "10:10"

    def test_multiple_transitions_produce_multiple_segments(self):
        readings = [
            {"congestion_level": "LOW", "recorded_at": "10:00"},
            {"congestion_level": "LOW", "recorded_at": "10:05"},
            {"congestion_level": "MODERATE", "recorded_at": "10:10"},
            {"congestion_level": "HIGH", "recorded_at": "10:15"},
        ]
        result = build_congestion_state_history(readings)
        assert len(result) == 3
        assert result[0]["congestion_level"] == "LOW"
        assert result[1]["congestion_level"] == "MODERATE"
        assert result[2]["congestion_level"] == "HIGH"

    def test_segment_boundaries_are_correct(self):
        readings = [
            {"congestion_level": "LOW", "recorded_at": "10:00"},
            {"congestion_level": "LOW", "recorded_at": "10:05"},
            {"congestion_level": "MODERATE", "recorded_at": "10:10"},
        ]
        result = build_congestion_state_history(readings)
        # first segment should span from the first LOW to the last LOW before the change
        assert result[0]["from"] == "10:00"
        assert result[0]["to"] == "10:05"
        # second segment starts exactly where the level changed
        assert result[1]["from"] == "10:10"
