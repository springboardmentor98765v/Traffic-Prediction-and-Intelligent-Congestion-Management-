"""
Proxy router for the Route Analysis Service (Intern 1 - Milestone 2).
Forwards requests from the API Gateway (port 8080) to the Route Analysis Service (port 8002).
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
import httpx
from ..config import settings
from ..auth.dependencies import get_current_user

router = APIRouter()

async def _route_forwarder(path: str, request: Request):
    url = f"{settings.ROUTE_ANALYSIS_URL}/api/v1/route/{path}"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.get(url, params=request.query_params)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"route_analysis returned error: {response.text}"
                )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail={"error": "route_analysis unreachable", "upstream": url, "exception": str(e)}
        )

@router.get("/optimize")
async def optimize_route(origin: str, destination: str, request: Request, user=Depends(get_current_user)):
    """Get the optimal driving route."""
    return await _route_forwarder("optimize", request)

@router.get("/alternate")
async def alternate_routes(origin: str, destination: str, request: Request, max_routes: int = 3, user=Depends(get_current_user)):
    """Get alternative candidate routes."""
    return await _route_forwarder("alternate", request)

@router.get("/travel-time")
async def travel_time(route_id: str, request: Request, user=Depends(get_current_user)):
    """Get travel time and ETA for a specific route."""
    return await _route_forwarder("travel-time", request)

@router.get("/conditions")
async def road_conditions(road_id: str, request: Request, user=Depends(get_current_user)):
    """Get live corridor conditions."""
    return await _route_forwarder("conditions", request)
