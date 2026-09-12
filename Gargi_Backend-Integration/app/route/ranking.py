def calculate_base_score(
    duration_minutes: float,
    distance_km: float,
) -> float:
    if distance_km <= 0:
        return 1.0

    average_speed = distance_km / (duration_minutes / 60)

    if average_speed >= 40:
        return 0.20

    if average_speed >= 30:
        return 0.40

    if average_speed >= 20:
        return 0.60

    if average_speed >= 10:
        return 0.80

    return 1.0


def calculate_traffic_factor(
    density: float,
) -> float:
    if density >= 0.85:
        return 1.00

    if density >= 0.65:
        return 0.75

    if density >= 0.50:
        return 0.50

    if density >= 0.30:
        return 0.25

    return 0.10


def calculate_congestion_score(
    duration_minutes: float,
    distance_km: float,
    traffic_density: float,
) -> float:
    base_score = calculate_base_score(
        duration_minutes,
        distance_km,
    )

    traffic_factor = calculate_traffic_factor(traffic_density)

    score = base_score * 0.4 + traffic_factor * 0.6

    return min(
        round(score, 2),
        1.0,
    )
