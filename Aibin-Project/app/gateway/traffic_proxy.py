"""
Proxy router for the Traffic Monitoring service (Intern 2 - anmol-data).
Forwards requests to the real service on port 8000, or falls back to mock data if it's down.
"""

from fastapi import APIRouter, Depends, Request, HTTPException
import httpx
from ..config import settings
from ..auth.dependencies import require_role

router = APIRouter()

# Allow both admin and traffic_operator to access
async def _fetch_from_upstream(full_path: str, request: Request):
    """Helper to forward the request to the upstream anmol-data service."""
    url = f"{settings.TRAFFIC_SERVICE_URL}/traffic/{full_path}"
    
    try:
        async with httpx.AsyncClient(timeout=40.0) as client:
            response = await client.get(url, params=request.query_params)
            
            # If the upstream returned a non-success status, forward that error
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"anmol-data returned error: {response.text}"
                )
            return response.json()
    except (httpx.RequestError) as e:
        # Surface reachability issues as 502 Bad Gateway
        raise HTTPException(
            status_code=502,
            detail={"error": "anmol-data unreachable", "upstream": url, "exception": str(e)}
        )

@router.get("/live")
async def get_live_traffic(request: Request, user=Depends(require_role(["admin", "traffic_operator"]))):
    """Get live traffic readings across all sensors."""
    return await _fetch_from_upstream("live", request)

@router.get("/density")
async def get_density_metrics(request: Request, user=Depends(require_role(["admin", "traffic_operator"]))):
    """Get overall density metrics for the city."""
    return await _fetch_from_upstream("density", request)

@router.get("/road/{road_id}")
async def get_road_details(road_id: str, request: Request, user=Depends(require_role(["admin", "traffic_operator"]))):
    """Get specific details and history for a given road."""
    return await _fetch_from_upstream(f"road/{road_id}", request)

@router.get("/{full_path:path}")
async def traffic_proxy_catchall(full_path: str, request: Request, user=Depends(require_role(["admin", "traffic_operator"]))):
    """
    Catch-all proxy route for forwarding any other traffic monitoring requests.
    """
    return await _fetch_from_upstream(full_path, request)

