from fastapi import APIRouter, Depends, Request, Header, HTTPException
import httpx
from ..config import settings
from ..auth.dependencies import get_current_user

router = APIRouter()

ALERT_SERVICE_URL = "http://127.0.0.1:8003" # Or use env var

async def _forward_request(method: str, path: str, request: Request, user):
    """Helper to forward requests and preserve status codes."""
    url = f"{ALERT_SERVICE_URL}/api/v1/alerts{path}"
    headers = {"x-user-id": str(user.id), "x-user-role": user.role}
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=request.query_params)
        elif method == "POST":
            # For POST requests, we need to read the body and forward it
            body = await request.body()
            response = await client.post(url, headers=headers, content=body)
            
        if response.status_code >= 400:
            # Try to extract the detail message if it's JSON
            try:
                detail = response.json().get("detail", response.text)
            except:
                detail = response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
            
        return response.json()

@router.get("/my")
async def get_my_alerts(request: Request, user=Depends(get_current_user)):
    """Fetch user's alerts from the Alert Service, passing RBAC details."""
    return await _forward_request("GET", "/my", request, user)

@router.post("/{alert_id}/read")
async def mark_alert_read(alert_id: int, request: Request, user=Depends(get_current_user)):
    """Mark alert read in the Alert Service."""
    return await _forward_request("POST", f"/{alert_id}/read", request, user)

@router.get("/active")
async def get_active_alerts(request: Request, user=Depends(get_current_user)):
    """Fetch active alerts from the Alert Service."""
    return await _forward_request("GET", "/active", request, user)

from pydantic import BaseModel
from typing import Optional

class AlertCreateProxy(BaseModel):
    type: str
    severity: str
    road_id: str
    message: str

@router.post("")
async def create_alert(alert: AlertCreateProxy, request: Request, user=Depends(get_current_user)):
    """Internal endpoint: called by threshold/anomaly feeds to create an alert."""
    url = f"{ALERT_SERVICE_URL}/api/v1/alerts"
    headers = {"x-user-id": str(user.id), "x-user-role": user.role}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=alert.model_dump())
        
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except:
                detail = response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
            
        return response.json()
