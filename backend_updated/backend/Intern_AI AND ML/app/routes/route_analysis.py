from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.maps_wrapper import maps_service
from app.routes.predict import predict_congestion
from app.routes.auth import get_current_user  # RBAC authentication dependency

router = APIRouter(tags=["Route Analysis"])


def validate_lat_lng(coord_str: str, field_name: str) -> tuple[float, float]:
    """Helper function to validate latitude and longitude format and range."""
    try:
        parts = coord_str.split(",")
        if len(parts) != 2:
            raise ValueError("Format must be lat,lng")

        lat, lng = float(parts[0].strip()), float(parts[1].strip())

        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValueError("Coordinates out of range")

        return lat, lng
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid {field_name}. Latitude must be between -90 and 90, and longitude "
                "between -180 and 180 (Format: lat,lng e.g. 11.9416,79.8083)."
            ),
        )


@router.get("/optimize")
async def optimize_route(
    origin: str = Query(..., description="Format: lat,lng e.g. 11.9416,79.8083"),
    destination: str = Query(..., description="Format: lat,lng e.g. 11.9350,79.8100"),
    current_user: dict = Depends(get_current_user),  # Enforces RBAC check
):
    orig_lat, orig_lng = validate_lat_lng(origin, "origin")
    dest_lat, dest_lng = validate_lat_lng(destination, "destination")

    route_data = await maps_service.get_route_geometry(orig_lat, orig_lng, dest_lat, dest_lng)

    ml_prediction = predict_congestion(
        road_id="R001",
        vehicle_count=35.0,
        density=12.0,
        avg_speed_kmph=40.0,
        road_capacity=100.0,
        road_length_km=route_data.get("distance_km", 2.0),
        hour=14,
        day_of_week=2,
        is_weekend=0,
    )

    return {
        "route_id": "route-opt-01",
        "path": route_data["geometry"].get("coordinates", []),
        "distance_km": route_data["distance_km"],
        "congestion_score": (
            getattr(ml_prediction, "confidence", 1.2)
            if not isinstance(ml_prediction, dict)
            else ml_prediction.get("confidence", 1.2)
        ),
        "predicted_level": (
            getattr(ml_prediction, "predicted_level", "Low")
            if not isinstance(ml_prediction, dict)
            else ml_prediction.get("predicted_level", "Low")
        ),
        "generated_by": "model-v1",
        "authorized_user": current_user.get("username"),
    }


@router.get("/alternate")
async def alternate_routes(
    origin: str = Query(..., description="Format: lat,lng e.g. 11.9416,79.8083"),
    destination: str = Query(..., description="Format: lat,lng e.g. 11.9350,79.8100"),
    current_user: dict = Depends(get_current_user),  # Enforces RBAC check
):
    orig_lat, orig_lng = validate_lat_lng(origin, "origin")
    dest_lat, dest_lng = validate_lat_lng(destination, "destination")

    routes = await maps_service.get_alternate_routes(orig_lat, orig_lng, dest_lat, dest_lng)

    # DEF-M3-004 Fix: Handle OSRM down / None fallback gracefully
    if not routes:
        raise HTTPException(
            status_code=503,
            detail="External maps service (OSRM) is currently unavailable. Please try again later.",
        )

    ranked_routes = []
    congestion_weights = {"Low": 1, "Medium": 2, "High": 3}

    for idx, route in enumerate(routes if isinstance(routes, list) else [routes]):
        ml_prediction = predict_congestion(
            road_id=f"R00{idx + 1}",
            vehicle_count=40.0 + (idx * 10),
            density=14.0 + (idx * 5),
            avg_speed_kmph=max(20.0, 45.0 - (idx * 10)),
            road_capacity=100.0,
            road_length_km=route.get("distance_km", 2.5),
            hour=14,
            day_of_week=2,
            is_weekend=0,
        )

        pred_level = (
            getattr(ml_prediction, "predicted_level", "Low")
            if not isinstance(ml_prediction, dict)
            else ml_prediction.get("predicted_level", "Low")
        )
        conf = (
            getattr(ml_prediction, "confidence", 0.8)
            if not isinstance(ml_prediction, dict)
            else ml_prediction.get("confidence", 0.8)
        )

        route["predicted_level"] = pred_level
        route["confidence"] = conf
        route["generated_by"] = "model-v1"
        route["sort_weight"] = congestion_weights.get(pred_level, 2)

        ranked_routes.append(route)

    ranked_routes.sort(key=lambda x: (x["sort_weight"], -x.get("distance_km", 0)))

    return {
        "status": "success",
        "authorized_user": current_user.get("username"),
        "total_routes": len(ranked_routes),
        "ranked_routes": ranked_routes,
    }


@router.get("/travel-time")
async def get_travel_time(
    origin: str = Query(..., description="Format: lat,lng e.g. 11.9416,79.8083"),
    destination: str = Query(..., description="Format: lat,lng e.g. 11.9350,79.8100"),
    current_user: dict = Depends(get_current_user),
):
    orig_lat, orig_lng = validate_lat_lng(origin, "origin")
    dest_lat, dest_lng = validate_lat_lng(destination, "destination")

    duration_mins = await maps_service.get_travel_duration(orig_lat, orig_lng, dest_lat, dest_lng)

    return {
        "origin": origin,
        "destination": destination,
        "estimated_minutes": round(duration_mins, 2),
        "based_on": "live+predicted",
    }


@router.get("/conditions")
async def get_road_conditions(
    origin: str = Query(..., description="Format: lat,lng e.g. 11.9416,79.8083"),
    destination: str = Query(..., description="Format: lat,lng e.g. 11.9350,79.8100"),
    current_user: dict = Depends(get_current_user),
):
    orig_lat, orig_lng = validate_lat_lng(origin, "origin")
    dest_lat, dest_lng = validate_lat_lng(destination, "destination")

    return {
        "origin": origin,
        "destination": destination,
        "status": "CLEAR",
        "hazards": [],
        "road_work_present": False,
    }
