from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum
import os

from app.database import get_db  
from app.models.alert import Alert  
from app.routes.auth import get_current_user



router = APIRouter(tags=["Alerts"])

# Optional bearer schema so it doesn't auto-error when missing (DEF-M3-025)
optional_bearer = HTTPBearer(auto_error=False)

# Strict environment variable check without hardcoded fallback
ALERT_SERVICE_KEY = os.getenv("ALERT_SERVICE_KEY")
if not ALERT_SERVICE_KEY:
    raise RuntimeError("CRITICAL: ALERT_SERVICE_KEY environment variable is not set.")

# Enum for strict severity validation (DEF-M3-008)
class SeverityEnum(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"

# Pydantic schema for incoming requests
class AlertCreate(BaseModel):
    type: str
    severity: SeverityEnum
    road_id: str
    message: str

# Pydantic schema for returning alert responses (Updated with ConfigDict for Pydantic v2)
class AlertResponse(BaseModel):
    alert_id: int
    type: str
    severity: str
    road_id: str
    message: str
    read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

@router.post("/", status_code=201)
def create_alert(
    alert_data: AlertCreate, 
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer)
):
    """
    Receives automated alerts and saves them directly into the database.
    Accepts EITHER a valid X-Alert-Service-Key / X-Service-Key header OR an operator/admin JWT token (DEF-M3-025).
    """
    authorized = False

    # Extract service key from either header variant sent by producers/watchers
    service_key_header = request.headers.get("x-alert-service-key") or request.headers.get("x-service-key")

    # 1. Check Service Key header
    if service_key_header and service_key_header == ALERT_SERVICE_KEY:
        authorized = True

    # 2. Alternatively, check if operator/admin provided a valid JWT token
    elif credentials:
        try:
            from app.routes.auth import decode_access_token
            token = credentials.credentials
            payload = decode_access_token(token)
            user_role = (payload.get("role") or "").lower()
            if user_role in ("operator", "admin"):
                authorized = True
        except Exception:
            pass

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Forbidden: Requires valid X-Alert-Service-Key header or operator/admin authentication."
        )

    try:
        new_alert = Alert(
            type=alert_data.type,
            severity=alert_data.severity.value,
            road_id=alert_data.road_id,
            message=alert_data.message,
            read=False,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        
        return {
            "alert_id": new_alert.alert_id,
            "status": "created",
            "road_id": new_alert.road_id,
            "message": "Alert successfully stored in database." 
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.get("/my", response_model=List[AlertResponse])
def get_my_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetches user-scoped alerts based on the JWT token role (DEF-M3-024). 
    Only operators and admins can see Critical alerts. Public/users are filtered out.
    """
    role = (current_user.get("role") or "").lower()
    query = db.query(Alert)
    
    if role not in ("operator", "admin"):
        query = query.filter(Alert.severity != "Critical")
        
    alerts = query.order_by(Alert.created_at.desc()).all()
    return alerts

@router.patch("/{alert_id}/read", status_code=200)
def mark_alert_as_read(
    alert_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Marks a specific alert as read (DEF-M3-005). 
    Intentionally allowed for authenticated users, operators, and admins.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.read = True
    db.commit()
    db.refresh(alert)
    
    return {
        "alert_id": alert.alert_id,
        "read": alert.read,
        "message": "Alert marked as read successfully."
    }