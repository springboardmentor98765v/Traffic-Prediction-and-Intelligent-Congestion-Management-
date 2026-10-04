from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.alerts.schemas import (
    AlertCreate,
    AlertCreateResponse,
    AlertReadResponse,
    AlertResponse,
)
from app.alerts.service import (
    create_alert,
    get_active_alerts,
    get_my_alerts,
    mark_alert_as_read,
)
from app.auth.dependencies import require_role
from app.auth.router import get_current_user
from app.database.connection import get_db
from app.database.models import User


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.post(
    "",
    response_model=AlertCreateResponse,
    status_code=201,
)
def create_alert_endpoint(
    alert: AlertCreate,
    db: Session = Depends(get_db),
):
    created_alert = create_alert(
        db=db,
        alert_type=alert.type,
        severity=alert.severity,
        road_id=alert.road_id,
        message=alert.message,
    )

    if not created_alert:
        raise HTTPException(
            status_code=404,
            detail="Road not found",
        )

    return {
        "alert_id": created_alert.id,
    }


@router.get(
    "/my",
    response_model=list[AlertResponse],
)
def get_my_alerts_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_my_alerts(
        db=db,
        user_id=current_user.id,
    )


@router.post(
    "/{alert_id}/read",
    response_model=AlertReadResponse,
)
def mark_alert_read_endpoint(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipient = mark_alert_as_read(
        db=db,
        alert_id=alert_id,
        user_id=current_user.id,
    )

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Alert not found for current user",
        )

    return {
        "alert_id": alert_id,
        "read": True,
    }


@router.get(
    "/active",
    response_model=list[AlertResponse],
)
def get_active_alerts_endpoint(
    current_user: User = Depends(require_role("admin", "operator")),
    db: Session = Depends(get_db),
):
    alerts = get_active_alerts(db)

    return [
        {
            "alert_id": alert.id,
            "type": alert.type,
            "severity": alert.severity,
            "road_id": alert.road_id,
            "message": alert.message,
            "read": False,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]

