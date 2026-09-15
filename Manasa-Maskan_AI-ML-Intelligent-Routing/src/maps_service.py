import requests


OSRM_BASE_URL = "https://router.project-osrm.org"


def get_routes(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
):
    """
    Get driving routes between two locations
    using the free OSRM routing service.

    Returns the best route and available alternatives.
    """

    coordinates = (
        f"{origin_lng},{origin_lat};"
        f"{destination_lng},{destination_lat}"
    )

    url = f"{OSRM_BASE_URL}/route/v1/driving/{coordinates}"

    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false",
        "alternatives": "true",
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        raise ValueError("Unable to find a route.")

    routes = []

    for index, route in enumerate(data.get("routes", []), start=1):
        routes.append(
            {
                "route_id": f"route_{index}",
                "distance_km": round(
                    route["distance"] / 1000,
                    2,
                ),
                "estimated_minutes": round(
                    route["duration"] / 60,
                    2,
                ),
                "geometry": route["geometry"],
            }
        )

    if not routes:
        raise ValueError("No routes were found.")

    return routes


def get_route(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
):
    """
    Get the best route between two locations.
    """

    routes = get_routes(
        origin_lat,
        origin_lng,
        destination_lat,
        destination_lng,
    )

    return routes[0]