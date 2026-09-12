import uuid

from sqlalchemy.orm import Session

from app.database.models import TrafficRecord
from app.route.maps import maps_service
from app.route.ranking import calculate_congestion_score
from app.route.storage import (
    get_route,
    save_route,
)


def get_current_traffic_density(
    db: Session,
) -> float:
    records = (
        db.query(TrafficRecord)
        .order_by(TrafficRecord.recorded_at.desc())
        .limit(3)
        .all()
    )

    if not records:
        return 0.0

    total_density = sum(record.density for record in records)

    return total_density / len(records)


def convert_geometry_to_path(geometry):
    coordinates = geometry.get(
        "coordinates",
        [],
    )

    return [
        {
            "lat": coordinate[1],
            "lng": coordinate[0],
        }
        for coordinate in coordinates
    ]


def build_route(
    route_data,
    traffic_density,
):
    distance_km = route_data["distance"] / 1000

    duration_minutes = route_data["duration"] / 60

    path = convert_geometry_to_path(route_data["geometry"])

    congestion_score = calculate_congestion_score(
        duration_minutes,
        distance_km,
        traffic_density,
    )

    route = {
        "route_id": (f"route-{uuid.uuid4().hex[:8]}"),
        "path": path,
        "distance_km": round(
            distance_km,
            2,
        ),
        "duration_minutes": round(
            duration_minutes,
            2,
        ),
        "congestion_score": congestion_score,
    }

    save_route(route)

    return route


def optimize_route(
    db: Session,
    origin_lat,
    origin_lng,
    destination_lat,
    destination_lng,
):
    data = maps_service.get_route(
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
        alternatives=False,
    )

    routes = data.get(
        "routes",
        [],
    )

    if not routes:
        raise ValueError("No route found")

    traffic_density = get_current_traffic_density(db)

    return build_route(
        routes[0],
        traffic_density,
    )


def get_alternate_routes(
    db: Session,
    origin_lat,
    origin_lng,
    destination_lat,
    destination_lng,
):
    data = maps_service.get_route(
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
        alternatives=True,
    )

    routes = data.get(
        "routes",
        [],
    )

    if not routes:
        raise ValueError("No routes found")

    traffic_density = get_current_traffic_density(db)

    result = []

    for route in routes:
        route_data = build_route(
            route,
            traffic_density,
        )

        result.append(route_data)

    result.sort(key=lambda route: route["congestion_score"])

    for index, route in enumerate(result):
        route["rank"] = index + 1

    return result


def get_travel_time(
    route_id: str,
):
    route = get_route(route_id)

    if not route:
        raise ValueError(f"Route {route_id} not found")

    base_time = route["duration_minutes"]

    congestion_score = route["congestion_score"]

    delay_factor = 1 + (congestion_score * 0.5)

    estimated_minutes = base_time * delay_factor

    return {
        "route_id": route_id,
        "estimated_minutes": round(
            estimated_minutes,
            2,
        ),
        "based_on": "live+predicted",
    }
