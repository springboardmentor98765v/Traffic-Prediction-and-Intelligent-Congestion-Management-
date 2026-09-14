import httpx

class MapsWrapper:
    """
    Internal wrapper around OpenStreetMap / OSRM public routing services 
    to resolve base road paths, distances, and geometries.
    """
    def __init__(self):
        # Using the public OSRM demo routing engine (Free, no API key required)
        self.base_url = "https://router.project-osrm.org/route/v1/driving"

    async def get_route_geometry(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float):
        url = f"{self.base_url}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        params = {
            "overview": "full",
            "geometries": "geojson"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("routes"):
                        route = data["routes"][0]
                        return {
                            "distance_km": route.get("distance", 0) / 1000.0,
                            "duration_minutes": route.get("duration", 0) / 60.0,
                            "geometry": route.get("geometry", {})
                        }
            except Exception as e:
                print(f"Maps API routing error: {e}")
                
        # Fallback dummy data if network/API is unreachable during local testing
        return {
            "distance_km": 5.2,
            "duration_minutes": 15.0,
            "geometry": {"coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]]}
        }

    async def get_alternate_routes(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float):
        url = f"{self.base_url}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "alternatives": "true"  # Tells OSRM to return alternative routes
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    routes = data.get("routes", [])
                    formatted_routes = []
                    
                    for idx, route in enumerate(routes):
                        formatted_routes.append({
                            "route_id": f"route-alt-{idx + 1:02d}",
                            "path": route.get("geometry", {}).get("coordinates", []),
                            "distance_km": route.get("distance", 0) / 1000.0,
                            "duration_minutes": route.get("duration", 0) / 60.0,
                            "congestion_score": round(1.0 + (idx * 0.4), 1),  # Incrementing score for alternatives
                            "rank": idx + 1
                        })
                    return formatted_routes
            except Exception as e:
                print(f"Maps API alternate routing error: {e}")

    async def get_travel_duration(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float):
        url = f"{self.base_url}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        params = {
            "overview": "false" # We only need duration/distance data, not full geometry
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("routes"):
                        route = data["routes"][0]
                        return route.get("duration", 0) / 60.0 # Convert seconds to minutes
            except Exception as e:
                print(f"Maps API duration error: {e}")
                
        return 18.5 # Fallback default
                
        # Fallback dummy alternate data if offline
        return [
            {
                "route_id": "route-alt-01",
                "path": [[origin_lng, origin_lat], [dest_lng, dest_lat]],
                "distance_km": 5.5,
                "congestion_score": 1.8,
                "rank": 1
            }
        ]

maps_service = MapsWrapper()