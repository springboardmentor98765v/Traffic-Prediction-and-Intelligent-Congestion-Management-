"""
Milestone 2 Day 5: Congestion-Aware Route-Ranking Engine.
Evaluates candidate routes supplied by Route Analysis (Intern 1)
and ranks them based on cumulative predicted ML delay and congestion penalties.
"""
from typing import List, Dict, Any
from datetime import datetime


CONGESTION_WEIGHTS = {
    "LOW": 1.0,
    "MEDIUM": 1.5,
    "HIGH": 2.5,
    "SEVERE": 4.0,
}


def rank_candidate_routes(
    candidate_routes: List[Dict[str, Any]],
    current_time: str = None,
    predict_fn=None,
) -> List[Dict[str, Any]]:
    """
    Ranks candidate routes by scoring total transit time + predicted ML congestion delay.

    Each candidate route structure expected:
    {
        "route_id": "route_A",
        "segments": [
            {"road_id": "1", "base_duration_min": 10.0, "density": 0.85, "vehicle_count": 120},
            {"road_id": "2", "base_duration_min": 8.0, "density": 0.30, "vehicle_count": 40}
        ]
    }
    """
    scored_routes = []

    for route in candidate_routes:
        route_id = route.get("route_id", "unknown")
        segments = route.get("segments", [])

        total_base_duration = 0.0
        total_predicted_delay = 0.0
        max_congestion = "LOW"
        segment_breakdowns = []

        for seg in segments:
            road_id = str(seg.get("road_id"))
            base_duration = float(seg.get("base_duration_min", 5.0))
            density = float(seg.get("density", 0.5))
            vehicle_count = int(seg.get("vehicle_count", 50))

            total_base_duration += base_duration

            # Query ML model inference
            if predict_fn:
                pred = predict_fn(
                    road_id=road_id,
                    time_str=current_time,
                    density=density,
                    vehicle_count=vehicle_count,
                )
                pred_level = pred["predicted_level"]
                delay = pred["estimated_delay_minutes"]
            else:
                pred_level = "LOW"
                delay = 0.0

            total_predicted_delay += delay

            # Track peak bottleneck level
            if CONGESTION_WEIGHTS.get(pred_level, 1.0) > CONGESTION_WEIGHTS.get(max_congestion, 1.0):
                max_congestion = pred_level

            segment_breakdowns.append({
                "road_id": road_id,
                "base_duration_min": base_duration,
                "predicted_congestion": pred_level,
                "predicted_delay_min": delay,
            })

        total_effective_eta = round(total_base_duration + total_predicted_delay, 2)

        scored_routes.append({
            "route_id": route_id,
            "total_effective_eta_min": total_effective_eta,
            "base_duration_min": round(total_base_duration, 2),
            "total_predicted_delay_min": round(total_predicted_delay, 2),
            "worst_segment_congestion": max_congestion,
            "segments_count": len(segments),
            "segment_breakdown": segment_breakdowns,
        })

    # Sort ascending: lowest effective ETA gets rank 1 (optimal)
    scored_routes.sort(key=lambda r: r["total_effective_eta_min"])

    for rank, r in enumerate(scored_routes, start=1):
        r["rank"] = rank
        r["is_recommended"] = (rank == 1)

    return scored_routes