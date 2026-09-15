from .maps_service import get_routes
from .ai_engine.predictor import (
    predict_traffic,
    get_traffic_condition,
)


# ---------------------------------------------------------
# Temporary route cache
# ---------------------------------------------------------

ROUTE_CACHE = {}


# ---------------------------------------------------------
# Route Analysis
# ---------------------------------------------------------

def analyze_routes(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
):
    """
    Get available routes from the maps service.

    This function provides the real map-based routes.
    AI congestion ranking is performed separately when
    road/junction information is available.
    """

    routes = get_routes(
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
    )

    analyzed_routes = []

    for index, route in enumerate(routes, start=1):

        analyzed_route = {
            "route_id": route["route_id"],
            "rank": index,
            "distance_km": route["distance_km"],
            "estimated_minutes": route["estimated_minutes"],
            "geometry": route["geometry"],
        }

        analyzed_routes.append(analyzed_route)

        # Store route for travel-time lookup
        ROUTE_CACHE[route["route_id"]] = analyzed_route

    return analyzed_routes


# ---------------------------------------------------------
# Congestion-Aware Route Ranking
# ---------------------------------------------------------

def rank_routes_with_congestion(
    routes,
    junction_ids,
    hour: int,
    day_of_week: int,
    month: int,
):
    """
    Rank candidate routes using the trained AI traffic model.

    Each route must have a corresponding junction ID.
    """

    if len(routes) != len(junction_ids):
        raise ValueError(
            "The number of routes and junction IDs must match."
        )

    ranked_routes = []

    for route, junction_id in zip(routes, junction_ids):

        predicted_vehicles = predict_traffic(
            junction_id,
            hour,
            day_of_week,
            month,
        )

        traffic_condition = get_traffic_condition(
            predicted_vehicles
        )

        if traffic_condition == "High Traffic":
            estimated_delay = 15

        elif traffic_condition == "Medium Traffic":
            estimated_delay = 8

        else:
            estimated_delay = 3

        ranked_route = {
            "route_id": route["route_id"],
            "junction_id": junction_id,
            "distance_km": route["distance_km"],
            "estimated_minutes": route["estimated_minutes"],
            "predicted_vehicle_count": predicted_vehicles,
            "traffic_condition": traffic_condition,
            "estimated_delay_minutes": estimated_delay,
            "geometry": route["geometry"],
        }

        ranked_routes.append(ranked_route)

    # Lower predicted congestion and lower delay
    # receive a better ranking.
    ranked_routes.sort(
        key=lambda route: (
            route["estimated_delay_minutes"],
            route["predicted_vehicle_count"],
            route["estimated_minutes"],
        )
    )

    for index, route in enumerate(ranked_routes, start=1):
        route["rank"] = index

    return ranked_routes


# ---------------------------------------------------------
# Best Route
# ---------------------------------------------------------

def get_best_route(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
):
    """
    Return the best map-based route.
    """

    routes = analyze_routes(
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
    )

    return routes[0]


# ---------------------------------------------------------
# Travel Time
# ---------------------------------------------------------

def get_travel_time(route_id: str):
    """
    Return estimated travel time for a calculated route.
    """

    route = ROUTE_CACHE.get(route_id)

    if route is None:
        raise ValueError(
            "Route not found. Please calculate the route first."
        )

    return {
        "route_id": route_id,
        "estimated_minutes": route["estimated_minutes"],
        "based_on": "map route estimation",
    }


# ---------------------------------------------------------
# Road Conditions
# ---------------------------------------------------------

def get_road_condition(
    road_id: int,
    status: str = "Unknown",
    notes: str = "Road-condition data not yet available.",
):
    """
    Return road-condition information.

    Actual road-condition data will be supplied by
    the Data Engineering / Traffic Monitoring module.
    """

    return {
        "road_id": road_id,
        "status": status,
        "notes": notes,
    }