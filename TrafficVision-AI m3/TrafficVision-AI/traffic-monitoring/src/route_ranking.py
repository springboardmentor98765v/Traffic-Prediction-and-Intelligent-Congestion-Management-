"""
Smart Route Ranking Service

Ranks candidate routes using congestion level,
prediction confidence, estimated delay, and distance.
"""

CONGESTION_SCORE = {
    "Low": 0,
    "Medium": 1,
    "High": 2,
    "Severe": 3,
}


def congestion_score(level: str) -> float:
    """Convert congestion level into a numerical score."""
    return CONGESTION_SCORE.get(level, 3)


def calculate_route_score(
    congestion_level: str,
    confidence: float,
    delay_minutes: float,
    distance_km: float,
) -> float:
    """
    Calculate a lower-is-better route score.

    Congestion has the highest impact, followed by delay
    and then route distance.
    """

    congestion = congestion_score(congestion_level)

    confidence_penalty = 1 - confidence

    score = (
        congestion * 60
        + delay_minutes * 8
        + distance_km * 2
        + confidence_penalty * 10
    )

    return round(score, 2)


def rank_routes(routes: list[dict]) -> list[dict]:
    """
    Rank candidate routes from best to worst.

    Each route should contain:
        route_id
        distance_km
        congestion_level
        confidence
        delay_minutes
    """

    ranked_routes = []

    for route in routes:
        score = calculate_route_score(
            congestion_level=route["congestion_level"],
            confidence=float(route["confidence"]),
            delay_minutes=float(route["delay_minutes"]),
            distance_km=float(route["distance_km"]),
        )

        ranked_routes.append({
            **route,
            "route_score": score,
        })

    ranked_routes.sort(key=lambda route: route["route_score"])

    for index, route in enumerate(ranked_routes, start=1):
        route["rank"] = index

    return ranked_routes