"""
TrafficVision AI — Analytics Helper Functions (Milestone 3, Day 6)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Pulls the pure, testable logic out of main.py's Analytics endpoints
    into its own module — same pattern as congestion_logic.py and
    congestion_tracking.py from Milestones 1 and 2. This lets the
    heatmap grid-building logic be unit tested directly, without
    needing a live database connection.
"""

from typing import List, Dict, Tuple


def build_heatmap_grid(roads: List[Dict], time_buckets: List[int], raw_results: List[Dict]) -> List[List[float]]:
    """
    Reshapes flat (road_id, bucket, avg_density) rows into a proper
    2D grid: values[i][j] corresponds to roads[i] at time_buckets[j].

    Uses a (road_id, bucket) -> value lookup dictionary rather than
    positional/sequential assembly, so missing combinations (a road
    with no data for some particular bucket) don't misalign every
    subsequent value — verified explicitly in the tests below.

    Missing cells default to 0, keeping the grid a complete rectangle
    even with incomplete underlying data.
    """
    lookup = {(row["road_id"], row["bucket"]): row["avg_density"] for row in raw_results}

    values = []
    for road in roads:
        row_values = [lookup.get((road["road_id"], bucket), 0) for bucket in time_buckets]
        values.append(row_values)

    return values
