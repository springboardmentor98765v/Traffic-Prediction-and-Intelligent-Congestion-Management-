"""Threshold-based traffic congestion calculation."""


def calculate_congestion(vehicle_count: int, road_capacity: int) -> str:
    if road_capacity <= 0:
        raise ValueError("road_capacity must be greater than 0")

    ratio = vehicle_count / road_capacity

    if ratio < 0.50:
        return "Low"
    elif ratio <= 0.80:
        return "Medium"
    elif ratio <= 1.00:
        return "High"
    return "Severe"
