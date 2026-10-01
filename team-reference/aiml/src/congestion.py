ROAD_CAPACITY = 200


def calculate_congestion(speed):
    """
    Basic Milestone 1 congestion classification
    based on average vehicle speed.
    """

    if speed >= 40:
        return "LOW"
    elif speed >= 20:
        return "MEDIUM"
    else:
        return "HIGH"


def predict_congestion(vehicle_count, average_speed, hour, road_capacity=ROAD_CAPACITY):
    """
    Milestone 1 heuristic congestion prediction.
    """

    density = vehicle_count / road_capacity

    if density >= 1.0 or average_speed < 20:
        level = "HIGH"
        confidence = 0.90

    elif density >= 0.6 or average_speed < 35:
        level = "MEDIUM"
        confidence = 0.80

    else:
        level = "LOW"
        confidence = 0.85

    # Peak-hour adjustment
    if 8 <= hour <= 10 or 17 <= hour <= 19:
        if level == "LOW":
            level = "MEDIUM"
            confidence = 0.75

    return {
        "predicted_level": level,
        "confidence": confidence,
        "model_version": "heuristic-v0"
    }