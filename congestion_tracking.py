"""
TrafficVision AI — Congestion Tracking & Road Utilization (Day 4)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Two things the SRS asks for on Day 4:
      1. Road utilization analysis — how "full" a road is relative to
         its capacity, not just raw vehicle count.
      2. Congestion-tracking workflow — turn a list of individual
         readings into a "state history": when did this road move from
         LOW to MODERATE, how long did it stay in each state, etc.

    This works directly off the traffic_readings rows that
    ingest_live_data.py (Day 2) has been writing — no new tables needed.
"""

from typing import List, Dict


def calculate_road_utilization(vehicle_count: int, lanes: int, capacity_per_lane: int = 30) -> float:
    """
    Rough utilization % — how full the road is relative to a rule-of-thumb
    capacity per lane (default: 30 vehicles/lane is treated as "full").

    utilization = vehicle_count / (lanes * capacity_per_lane), capped at 100%
    """
    if lanes <= 0:
        return 0.0
    max_capacity = lanes * capacity_per_lane
    utilization = (vehicle_count / max_capacity) * 100
    return round(min(utilization, 100.0), 2)


def build_congestion_state_history(readings: List[Dict]) -> List[Dict]:
    """
    Takes a list of readings for ONE road, ordered OLDEST -> NEWEST,
    each with 'congestion_level' and 'recorded_at', and groups them into
    state segments: "this road was LOW from 10:00 to 10:15, then MODERATE
    from 10:15 to 10:30", etc.

    This is the "state history" the SRS asks for — instead of just a
    flat list of raw readings, it shows *transitions* between states,
    which is far more useful for a dashboard timeline view.
    """
    if not readings:
        return []

    segments = []
    current_level = readings[0]["congestion_level"]
    segment_start = readings[0]["recorded_at"]
    segment_end = readings[0]["recorded_at"]

    for reading in readings[1:]:
        level = reading["congestion_level"]
        timestamp = reading["recorded_at"]

        if level == current_level:
            # Still in the same state — just extend the end time
            segment_end = timestamp
        else:
            # State changed — close off the previous segment, start a new one
            segments.append({
                "congestion_level": current_level,
                "from": segment_start,
                "to": segment_end,
            })
            current_level = level
            segment_start = timestamp
            segment_end = timestamp

    # Close off the final segment
    segments.append({
        "congestion_level": current_level,
        "from": segment_start,
        "to": segment_end,
    })

    return segments


# ---------------------------------------------------------
# Quick self-test — run this file directly to sanity check
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Utilization test:")
    print(" 40 vehicles, 4 lanes ->", calculate_road_utilization(40, 4), "%")
    print(" 150 vehicles, 4 lanes ->", calculate_road_utilization(150, 4), "%")

    print("\nState history test:")
    sample_readings = [
        {"congestion_level": "LOW", "recorded_at": "10:00"},
        {"congestion_level": "LOW", "recorded_at": "10:05"},
        {"congestion_level": "MODERATE", "recorded_at": "10:10"},
        {"congestion_level": "MODERATE", "recorded_at": "10:15"},
        {"congestion_level": "HIGH", "recorded_at": "10:20"},
    ]
    for segment in build_congestion_state_history(sample_readings):
        print(" ", segment)
