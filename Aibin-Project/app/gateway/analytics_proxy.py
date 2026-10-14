from fastapi import APIRouter, Depends, Request
import httpx
from ..config import settings
from ..auth.dependencies import require_role

router = APIRouter()

# Forward analytics to anmol-data (Port 8000)
# As per spec:
# GET /api/v1/analytics/trends?road_id={id}&range=day|week (Intern 2)
# GET /api/v1/analytics/heatmap?range={range} (Intern 2)

async def _analytics_forwarder(path: str, request: Request):
    url = f"{settings.TRAFFIC_SERVICE_URL}/analytics/{path}"
    try:
        async with httpx.AsyncClient(timeout=40.0) as client:
            response = await client.get(url, params=request.query_params)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"anmol-data returned error: {response.text}"
                )
            
            # If it's the CSV stream, return a StreamingResponse
            if "csv" in response.headers.get("Content-Type", ""):
                from fastapi.responses import StreamingResponse
                async def stream_generator():
                    async for chunk in response.aiter_bytes():
                        yield chunk
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="text/csv",
                    headers={"Content-Disposition": response.headers.get("Content-Disposition", "")}
                )
                
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail={"error": "anmol-data unreachable", "upstream": url, "exception": str(e)}
        )

@router.get("/trends")
async def get_traffic_trends(
    request: Request, 
    road_id: int | None = None,
    range: str = "week",
    user=Depends(require_role(["admin", "traffic_operator", "city_planner"]))
):
    """Proxy for Traffic Trends requests to Anmol's Data Service."""
    return await _analytics_forwarder("trends", request)

@router.get("/heatmap")
async def get_incident_heatmap(
    request: Request, 
    range: str = "week",
    road_id: int | None = None,
    bucket: str = "hour",
    user=Depends(require_role(["admin", "traffic_operator", "city_planner"]))
):
    """Proxy for Incident Heatmap requests to Anmol's Data Service."""
    return await _analytics_forwarder("heatmap", request)

@router.get("/reports")
async def get_traffic_reports(
    request: Request, 
    road_id: int | None = None,
    range: str = "week",
    format: str = "json",
    page: int = 1,
    page_size: int = 25,
    user=Depends(require_role(["admin", "traffic_operator", "city_planner"]))
):
    """Proxy for Traffic Reports requests to Anmol's Data Service."""
    return await _analytics_forwarder("reports", request)
