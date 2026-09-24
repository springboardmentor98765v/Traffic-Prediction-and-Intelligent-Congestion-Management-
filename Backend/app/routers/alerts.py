from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User, UserRole
from app.middleware.auth_middleware import get_current_user, get_optional_current_user, require_role
from app.schemas.alert import (
    AlertCreate, AlertResponse, AlertReadResponse,
    AlertCreateResponse, AlertPollResponse, TriggerAlertsResponse
)
from app.services import alert_service
from app.services.alert_service import ws_manager

router = APIRouter()


@router.post(
    "",
    response_model=AlertCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Alert (Internal & Feed Ingestion)",
    description=(
        "Internal and feed ingestion endpoint for creating alerts (congestion thresholds, "
        "AI anomalies, road closures, or operator triggers). Implements automatic deduplication "
        "and rate limiting to prevent notification noise."
    )
)
def create_new_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db)
):
    alert = alert_service.create_alert(db, alert_in)
    return {
        "alert_id": alert.id,
        "type": alert.type,
        "severity": alert.severity,
        "road_id": alert.road_id,
        "message": alert.message,
        "created_at": alert.created_at,
        "status": "created"
    }


@router.get(
    "/my",
    response_model=List[AlertResponse],
    summary="Get My Alerts (Role-Scoped Notifications)",
    description=(
        "Retrieve in-app notifications scoped by user role:\n"
        "- **Admin & Operator**: Full visibility over all system alerts, operational notices, and public alerts.\n"
        "- **Public Users & Guests**: Public safety alerts (accidents, road closures, delay warnings, severe congestion).\n"
        "Computes individual read status per user."
    )
)
def get_user_alerts(
    unread_only: bool = Query(False, description="Filter only unread alerts"),
    limit: int = Query(50, ge=1, le=100, description="Max alerts to retrieve"),
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    alerts = alert_service.get_my_alerts(
        db,
        user=user,
        unread_only=unread_only,
        limit=limit
    )
    return alerts


@router.post(
    "/{alert_id}/read",
    response_model=AlertReadResponse,
    summary="Mark Alert as Read",
    description="Marks a specific alert as read for the current user or globally."
)
def mark_alert_as_read(
    alert_id: str,
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    result = alert_service.mark_alert_read(db, alert_id=alert_id, user=user)
    return result


@router.get(
    "/active",
    response_model=List[AlertResponse],
    summary="Get Active Alerts (Dashboard Overview)",
    description="List all currently active alerts for Admin and Operator dashboards."
)
def get_active_alerts_list(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    alerts = alert_service.get_active_alerts(db, limit=limit)
    return alerts


@router.get(
    "/poll",
    response_model=AlertPollResponse,
    summary="Near-Real-Time REST Polling Delivery",
    description=(
        "Short-interval polling endpoint for responsive in-app notification bells.\n"
        "Supplying `since` returns newly created or updated alerts since the provided timestamp."
    )
)
def poll_alerts(
    since: Optional[datetime] = Query(None, description="ISO timestamp to fetch newer alerts"),
    unread_only: bool = Query(False, description="Only return unread alerts"),
    limit: int = Query(50, ge=1, le=100),
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    return alert_service.poll_alerts(
        db,
        user=user,
        since=since,
        unread_only=unread_only,
        limit=limit
    )


@router.post(
    "/evaluate-triggers",
    response_model=TriggerAlertsResponse,
    summary="Evaluate All Trigger Feeds (Internal/Operator)",
    description=(
        "Evaluates congestion threshold feeds, road closures/hazards, and AI anomalies, "
        "automatically generating corresponding alerts in the system."
    )
)
def evaluate_alert_triggers(
    user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    res = alert_service.evaluate_all_triggers(db)
    return {
        "triggered_count": res["total_triggered"],
        "alerts": res["alerts"],
        "details": res
    }


@router.websocket("/ws")
async def alerts_websocket_endpoint(websocket: WebSocket):
    """
    Stretch Goal: Real-time WebSocket channel for instant notification push.
    Clients connect to receive new alert events instantly without polling.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Simple heartbeat / ping-pong support
            if data.strip().lower() == "ping":
                await websocket.send_json({"event": "pong", "timestamp": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
