from .ai_engine.predictor import predict_traffic, get_traffic_condition


def optimize_routes(
    road_ids,
    hour,
    day_of_week,
    month,
):
    """
    Rank possible roads based on predicted traffic.

    The road with lower predicted traffic is ranked better.
    """

    routes = []

    for road_id in road_ids:

        # Predict traffic for this road
        predicted_vehicles = predict_traffic(
            road_id,
            hour,
            day_of_week,
            month,
        )

        # Convert prediction into traffic condition
        traffic_condition = get_traffic_condition(
            predicted_vehicles
        )

        # Estimate delay based on traffic condition
        if traffic_condition == "High Traffic":
            estimated_delay = 15

        elif traffic_condition == "Medium Traffic":
            estimated_delay = 8

        else:
            estimated_delay = 3

        routes.append(
            {
                "road_id": road_id,
                "predicted_vehicle_count": predicted_vehicles,
                "traffic_condition": traffic_condition,
                "estimated_delay_minutes": estimated_delay,
            }
        )

    # Rank roads by predicted traffic
    routes.sort(
        key=lambda route: (
            route["estimated_delay_minutes"],
            route["predicted_vehicle_count"],
        )
    )

    # Add ranking
    for index, route in enumerate(routes, start=1):
        route["rank"] = index

    return routes