"""
Proxy router for the AI Prediction Engine (Intern 3 - Milestone 2).
Forwards requests from the API Gateway (port 8080) to the AI Engine service (port 8001),
with graceful fallback if the standalone AI service is offline.
"""

from fastapi import APIRouter, Request, HTTPException, Query, status, Depends
from typing import Optional, Dict, Any
import httpx
from ..config import settings
from ..auth.dependencies import get_current_user

router = APIRouter()

@router.get("/congestion")
async def predict_congestion(
    road_id: str = Query(..., description="Identifier of the road segment"),
    time: Optional[str] = Query(None, description="ISO-8601 timestamp string"),
    density: float = Query(0.5, ge=0.0, le=1.0, description="Normalized traffic density"),
    vehicle_count: int = Query(50, ge=0, description="Observed vehicle count"),
    user=Depends(get_current_user)
):
    """Proxy for real-time congestion prediction."""
    url = f"{settings.AI_ENGINE_URL}/predict/congestion"
    params = {
        "road_id": road_id,
        "time": time,
        "density": density,
        "vehicle_count": vehicle_count
    }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.get("/delay")
async def predict_delay(
    road_id: str = Query(..., description="Identifier of the road segment"),
    time: Optional[str] = Query(None, description="ISO-8601 timestamp string"),
    density: float = Query(0.5, ge=0.0, le=1.0, description="Normalized traffic density"),
    vehicle_count: int = Query(50, ge=0, description="Observed vehicle count"),
    user=Depends(get_current_user)
):
    """Proxy for travel delay estimation."""
    url = f"{settings.AI_ENGINE_URL}/predict/delay"
    params = {
        "road_id": road_id,
        "time": time,
        "density": density,
        "vehicle_count": vehicle_count
    }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.get("/peak-hours")
async def get_peak_hours(hour: int = Query(..., ge=0, le=23), user=Depends(get_current_user)):
    """Proxy for peak-hour status detection."""
    url = f"{settings.AI_ENGINE_URL}/predict/peak-hours"
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={"hour": hour})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.post("/routes/rank")
async def rank_routes(payload: Dict[str, Any], user=Depends(get_current_user)):
    """Proxy for candidate route ranking."""
    url = f"{settings.AI_ENGINE_URL}/predict/routes/rank"
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.get("/anomalies")
async def detect_anomalies(
    road_id: str = Query(...),
    expected_level: str = Query(...),
    observed_level: str = Query(...),
    time: Optional[str] = Query(None),
    user=Depends(get_current_user)
):
    """Proxy for AI Anomaly Detection."""
    url = f"{settings.AI_ENGINE_URL}/ai/anomalies"
    params = {
        "road_id": road_id,
        "expected_level": expected_level,
        "observed_level": observed_level,
        "time": time
    }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})

@router.get("/recommendations")
async def get_recommendations(
    road_id: str = Query(...),
    time: Optional[str] = Query(None),
    density: float = Query(0.5, ge=0.0, le=1.0),
    vehicle_count: int = Query(50, ge=0),
    user=Depends(get_current_user)
):
    """Proxy for AI Recommendations."""
    url = f"{settings.AI_ENGINE_URL}/api/v1/ai/recommendations"
    params = {
        "road_id": road_id,
        "time": time,
        "density": density,
        "vehicle_count": vehicle_count
    }
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, params={k: v for k, v in params.items() if v is not None})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=f"saksham-aiml returned error: {resp.text}")
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail={"error": "saksham-aiml unreachable", "upstream": url, "exception": str(e)})
