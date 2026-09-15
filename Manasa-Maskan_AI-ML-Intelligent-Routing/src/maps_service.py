"""
TrafficVision AI - Maps / Routing Service

Uses the free OSRM routing API with OpenStreetMap road data.

This service provides:
- Route calculation
- Route distance
- Estimated travel time
- Alternative routes
- Route geometry
"""

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


# ---------------------------------------------------------
# OSRM Configuration
# ---------------------------------------------------------

OSRM_BASE_URL = "https://router.project-osrm.org"


# ---------------------------------------------------------
# Internal helper
# ---------------------------------------------------------

def _request_osrm(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    alternatives: bool = False,
):
    """
    Send a routing request to the public OSRM service.

    OSRM expects coordinates in:
    longitude,latitude
    """

    coordinates = (
        f"{origin_lon},{origin_lat};"
        f"{destination_lon},{destination_lat}"
    )

    url = (
        f"{OSRM_BASE_URL}/route/v1/driving/"
        f"{coordinates}"
    )

    params = urlencode(
        {
            "alternatives": str(alternatives).lower(),
            "overview": "full",
            "geometries": "geojson",
        }
    )

    request = Request(
        f"{url}?{params}",
        headers={
            "User-Agent": "TrafficVision-AI/1.0"
        },
    )

    with urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))

    if data.get("code") != "Ok":
        raise RuntimeError(
            f"OSRM routing failed: {data.get('code')}"
        )

    return data


# ---------------------------------------------------------
# Route calculation
# ---------------------------------------------------------

def get_routes(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    alternatives: bool = True,
):
    """
    Calculate routes between an origin and destination.

    Returns route information including:
    - distance in kilometres
    - estimated duration in minutes
    - route geometry
    """

    data = _request_osrm(
        origin_lat,
        origin_lon,
        destination_lat,
        destination_lon,
        alternatives=alternatives,
    )

    routes = []

    for index, route in enumerate(data.get("routes", []), start=1):

        distance_km = route["distance"] / 1000
        duration_minutes = route["duration"] / 60

        routes.append(
            {
                "route_id": index,
                "distance_km": round(distance_km, 2),
                "estimated_minutes": round(duration_minutes, 2),
                "geometry": route.get("geometry"),
            }
        )

    return routes


# ---------------------------------------------------------
# Single recommended route
# ---------------------------------------------------------

def get_route(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
):
    """
    Get the primary recommended route.
    """

    routes = get_routes(
        origin_lat,
        origin_lon,
        destination_lat,
        destination_lon,
        alternatives=False,
    )

    if not routes:
        raise RuntimeError("No route found")

    return routes[0]


# ---------------------------------------------------------
# Travel-time estimation
# ---------------------------------------------------------

def get_travel_time(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
):
    """
    Return estimated travel time and distance.
    """

    route = get_route(
        origin_lat,
        origin_lon,
        destination_lat,
        destination_lon,
    )

    return {
        "distance_km": route["distance_km"],
        "estimated_minutes": route["estimated_minutes"],
    }


# ---------------------------------------------------------
# Simple test
# ---------------------------------------------------------

if __name__ == "__main__":

    # Example coordinates.
    # These are only test coordinates.
    origin = (17.3850, 78.4867)
    destination = (17.4065, 78.4772)

    print("TrafficVision AI - OSRM Map Routing Test")
    print("------------------------------------------")

    routes = get_routes(
        origin[0],
        origin[1],
        destination[0],
        destination[1],
        alternatives=True,
    )

    for route in routes:
        print()
        print(f"Route {route['route_id']}")
        print(f"Distance: {route['distance_km']} km")
        print(
            f"Estimated time: "
            f"{route['estimated_minutes']} minutes"
        )

    print()
    print("OSRM routing test completed successfully.")