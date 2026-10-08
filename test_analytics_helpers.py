"""
TrafficVision AI — Unit Tests for analytics_helpers.py (Milestone 3, Day 6)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Run:
    pytest test_analytics_helpers.py -v
"""

import pytest
from analytics_helpers import build_heatmap_grid


class TestBuildHeatmapGrid:

    def test_complete_data_produces_correct_grid(self):
        roads = [{"road_id": 1, "road_name": "Anna Salai"}]
        time_buckets = [0, 1, 2]
        raw_results = [
            {"road_id": 1, "bucket": 0, "avg_density": 10.0},
            {"road_id": 1, "bucket": 1, "avg_density": 20.0},
            {"road_id": 1, "bucket": 2, "avg_density": 30.0},
        ]
        result = build_heatmap_grid(roads, time_buckets, raw_results)
        assert result == [[10.0, 20.0, 30.0]]

    def test_grid_is_always_a_proper_rectangle(self):
        """Every row must be exactly len(time_buckets) long, regardless of missing data."""
        roads = [{"road_id": 1, "road_name": "A"}, {"road_id": 2, "road_name": "B"}]
        time_buckets = [0, 1, 2, 3, 4]
        raw_results = [{"road_id": 1, "bucket": 0, "avg_density": 5.0}]  # sparse data

        result = build_heatmap_grid(roads, time_buckets, raw_results)

        assert len(result) == len(roads)
        for row in result:
            assert len(row) == len(time_buckets)

    def test_missing_cell_defaults_to_zero_not_dropped(self):
        roads = [{"road_id": 1, "road_name": "A"}]
        time_buckets = [0, 1, 2]
        raw_results = [
            {"road_id": 1, "bucket": 0, "avg_density": 10.0},
            # bucket 1 is missing entirely
            {"road_id": 1, "bucket": 2, "avg_density": 30.0},
        ]
        result = build_heatmap_grid(roads, time_buckets, raw_results)
        assert result == [[10.0, 0, 30.0]]

    def test_missing_cell_does_not_misalign_subsequent_values(self):
        """
        The critical regression test from Day 4's manual verification,
        now formalized: a gap in the middle of the data must not shift
        later values into the wrong column.
        """
        roads = [{"road_id": 1, "road_name": "A"}, {"road_id": 2, "road_name": "B"}]
        time_buckets = [0, 1, 2, 3, 4, 5, 6]
        raw_results = [
            {"road_id": 1, "bucket": 0, "avg_density": 20.1},
            {"road_id": 1, "bucket": 1, "avg_density": 25.3},
            {"road_id": 1, "bucket": 2, "avg_density": 30.0},
            {"road_id": 1, "bucket": 3, "avg_density": 40.5},
            {"road_id": 1, "bucket": 4, "avg_density": 42.0},
            {"road_id": 1, "bucket": 5, "avg_density": 38.0},
            {"road_id": 1, "bucket": 6, "avg_density": 22.0},
            {"road_id": 2, "bucket": 0, "avg_density": 15.0},
            {"road_id": 2, "bucket": 1, "avg_density": 18.0},
            {"road_id": 2, "bucket": 2, "avg_density": 20.0},
            # bucket 3 missing for road_id=2
            {"road_id": 2, "bucket": 4, "avg_density": 21.0},
            {"road_id": 2, "bucket": 5, "avg_density": 19.0},
            {"road_id": 2, "bucket": 6, "avg_density": 14.0},
        ]

        result = build_heatmap_grid(roads, time_buckets, raw_results)

        # road_id=2's row: bucket 3 -> 0, but bucket 4 must STILL be 21.0,
        # not shifted to where bucket 3's value would have been
        assert result[1][3] == 0
        assert result[1][4] == 21.0
        assert result[1][5] == 19.0
        assert result[1][6] == 14.0

    def test_empty_raw_results_produces_all_zero_grid(self):
        roads = [{"road_id": 1, "road_name": "A"}]
        time_buckets = [0, 1, 2]
        result = build_heatmap_grid(roads, time_buckets, [])
        assert result == [[0, 0, 0]]

    def test_row_order_matches_input_road_order(self):
        """The output grid's row order must match the roads list order, not arrival order in raw_results."""
        roads = [{"road_id": 2, "road_name": "B"}, {"road_id": 1, "road_name": "A"}]  # note: 2 before 1
        time_buckets = [0]
        raw_results = [
            {"road_id": 1, "bucket": 0, "avg_density": 100.0},
            {"road_id": 2, "bucket": 0, "avg_density": 200.0},
        ]
        result = build_heatmap_grid(roads, time_buckets, raw_results)
        assert result[0] == [200.0]  # road_id=2's row first, matching roads list order
        assert result[1] == [100.0]  # road_id=1's row second
