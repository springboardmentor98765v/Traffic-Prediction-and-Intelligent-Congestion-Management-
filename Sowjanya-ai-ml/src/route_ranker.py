def congestion_penalty(congestion_level):
    """
    Convert predicted congestion into a numeric penalty.
    Higher congestion = higher penalty.
    """

    level = str(congestion_level).upper()

    if level == "LOW":
        return 0

    elif level == "MEDIUM":
        return 5

    elif level == "HIGH":
        return 10

    return 5


def calculate_route_score(
    distance_km,
    estimated_delay_minutes,
    predicted_congestion
):
    """
    Calculate a route score using distance,
    predicted delay and congestion.
    
    Lower score = better route according to
    the ranking formula.
    """

    penalty = congestion_penalty(
        predicted_congestion
    )

    score = (
        distance_km
        + estimated_delay_minutes
        + penalty
    )

    return round(score, 2)


def rank_routes(routes):
    """
    Rank candidate routes based on congestion-aware score.

    Each route should contain:
    route_id
    distance_km
    estimated_delay_minutes
    predicted_congestion
    """

    ranked_routes = []

    for route in routes:

        score = calculate_route_score(
            distance_km=route["distance_km"],
            estimated_delay_minutes=route[
                "estimated_delay_minutes"
            ],
            predicted_congestion=route[
                "predicted_congestion"
            ]
        )

        ranked_routes.append({
            **route,
            "congestion_score": score
        })

    ranked_routes.sort(
        key=lambda x: x["congestion_score"]
    )

    for rank, route in enumerate(
        ranked_routes,
        start=1
    ):
        route["rank"] = rank

    return ranked_routes