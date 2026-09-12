import requests

OSRM_BASE_URL = "https://router.project-osrm.org"


class MapsService:

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        alternatives: bool = False,
    ):
        coordinates = (
            f"{origin_lng},{origin_lat};" f"{destination_lng},{destination_lat}"
        )

        url = f"{OSRM_BASE_URL}/route/v1/driving/{coordinates}"

        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
            "alternatives": "true" if alternatives else "false",
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("code") != "Ok":
            raise ValueError("Unable to find a route")

        return data


maps_service = MapsService()
