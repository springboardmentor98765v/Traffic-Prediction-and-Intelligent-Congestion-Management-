import hashlib
import json
import math
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Annotated

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")
PREDICTION_SERVICE_URL = os.getenv("PREDICTION_SERVICE_URL", "http://ai-engine:8003")
TRAFFIC_SERVICE_URL = os.getenv("TRAFFIC_SERVICE_URL", "http://traffic-monitoring:8002")
ROUTE_CACHE_FILE = Path(__file__).resolve().parent / "route_cache.json"


def load_route_cache() -> dict[str, dict]:
    if not ROUTE_CACHE_FILE.exists():
        return {}
    try:
        return json.loads(ROUTE_CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_route_cache() -> None:
    ROUTE_CACHE_FILE.write_text(
        json.dumps(ROUTE_CACHE, indent=2),
        encoding="utf-8",
    )


ROUTE_CACHE: dict[str, dict] = load_route_cache()

app = FastAPI(title="TrafficVision AI Route Analysis Service", version="2.0.0")


class Coordinate(BaseModel):
    lat: float
    lng: float

def parse_coordinate(value: str) -> Coordinate:
    try:
        lat, lng = (float(part.strip()) for part in value.split(","))
    except ValueError:
        raise HTTPException(status_code=422, detail="Coordinates must use lat,lng format")
    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
        raise HTTPException(status_code=422, detail="Coordinates are outside valid latitude/longitude bounds")
    return Coordinate(lat=lat, lng=lng)


def route_id(path: list[list[float]]) -> str:
    text = ";".join(f"{lat:.6f},{lng:.6f}" for lat, lng in path)
    return "route-" + hashlib.sha256(text.encode()).hexdigest()[:12]


def route_payload(route: dict) -> dict:
    # OSRM geometry coordinates are lng,lat.
    # TrafficVision exposes path as lat,lng.
    path = [
        [lat, lng]
        for lng, lat in route["geometry"]["coordinates"]
    ]

    identifier = route_id(path)

    payload = {
        "route_id": identifier,
        "path": path,
        "distance_km": round(route["distance"] / 1000, 2),
        "congestion_score": 0.0,
    }

    ROUTE_CACHE[identifier] = {
        **payload,
        "base_minutes": route["duration"] / 60,
    }

    save_route_cache()

    return payload

async def resolve_routes(origin: Coordinate, destination: Coordinate, alternatives: bool) -> list[dict]:
    coordinates = f"{origin.lng},{origin.lat};{destination.lng},{destination.lat}"
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coordinates}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params={"overview": "full", "geometries": "geojson", "alternatives": str(alternatives).lower()})
            response.raise_for_status()
            body = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(status_code=503, detail="Maps routing service unavailable") from error
    if body.get("code") != "Ok" or not body.get("routes"):
        raise HTTPException(status_code=404, detail="No drivable route found")
    return [route_payload(route) for route in body["routes"]]

async def predicted_congestion_score(route: dict) -> float:
    # M2 integration point: until Intern 3 provides road-segment prediction mapping,
    # distance is the safe fallback; score becomes prediction-driven once configured.
    return round(min(1.0, route["distance_km"] / 100), 2)


@app.get("/health")
def health():
    return {"status": "ok", "service": "route-analysis"}


@app.get("/api/v1/route/optimize")
async def optimize(
    origin: Annotated[str, Query()],
    destination: Annotated[str, Query()],
):
    routes = await resolve_routes(
        parse_coordinate(origin),
        parse_coordinate(destination),
        alternatives=False,
    )

    best = routes[0]
    best["congestion_score"] = await predicted_congestion_score(best)

    if best["route_id"] in ROUTE_CACHE:
        ROUTE_CACHE[best["route_id"]]["congestion_score"] = best["congestion_score"]
        save_route_cache()

    return best


@app.get("/api/v1/route/alternate")
async def alternate(
    origin: Annotated[str, Query()],
    destination: Annotated[str, Query()],
):
    routes = await resolve_routes(
        parse_coordinate(origin),
        parse_coordinate(destination),
        alternatives=True,
    )

    for route in routes:
        route["congestion_score"] = await predicted_congestion_score(route)

        if route["route_id"] in ROUTE_CACHE:
            ROUTE_CACHE[route["route_id"]]["congestion_score"] = route[
                "congestion_score"
            ]

    save_route_cache()

    return [
        {
            "route_id": item["route_id"],
            "path": item["path"],
            "congestion_score": item["congestion_score"],
            "rank": rank,
        }
        for rank, item in enumerate(
            sorted(
                routes,
                key=lambda value: (
                    value["congestion_score"],
                    value["distance_km"],
                ),
            ),
            start=1,
        )
    ]


@app.get("/api/v1/route/travel-time")
async def travel_time(route_id: str):
    route = ROUTE_CACHE.get(route_id)

    if not route:
        raise HTTPException(
            status_code=404,
            detail="Unknown route_id. Call /route/optimize or /route/alternate first",
        )

    estimated = route["base_minutes"] * (1 + route["congestion_score"])

    return {
        "route_id": route_id,
        "estimated_minutes": round(estimated, 1),
        "based_on": "live+predicted",
    }


@app.get("/api/v1/route/conditions")
async def conditions(road_id: str):
    url = f"{TRAFFIC_SERVICE_URL}/api/v1/traffic/road-condition/{road_id}"

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError:
        return {
            "road_id": road_id,
            "status": "unknown",
            "notes": "Road-condition feed unavailable",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
