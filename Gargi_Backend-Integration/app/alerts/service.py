from sqlalchemy.orm import Session

from app.database.models import (
    Alert,
    AlertRecipient,
    Road,
    User,
)
from app.prediction.service import prediction_service
from app.route.conditions import get_road_condition


PUBLIC_ALERT_TYPES = {
    "accident",
    "possible_incident",
    "road_closure",
    "closure",
    "delay",
}


def _is_public_alert(
    alert_type: str,
    severity: str,
) -> bool:
    normalized_type = alert_type.strip().lower()
    normalized_severity = severity.strip().lower()

    return (
        normalized_type in PUBLIC_ALERT_TYPES
        or normalized_severity == "high"
    )


def _create_recipients(
    db: Session,
    alert: Alert,
):
    users = (
        db.query(User)
        .filter(User.is_active.is_(True))
        .all()
    )

    public_alert = _is_public_alert(
        alert.type,
        alert.severity,
    )

    recipients = []

    for user in users:
        role_name = (
            user.role.name.lower()
            if user.role
            else None
        )

        if role_name in {"admin", "operator"}:
            recipients.append(
                AlertRecipient(
                    alert_id=alert.id,
                    user_id=user.id,
                    read=False,
                )
            )
        elif role_name == "public" and public_alert:
            recipients.append(
                AlertRecipient(
                    alert_id=alert.id,
                    user_id=user.id,
                    read=False,
                )
            )

    db.add_all(recipients)


def create_alert(
    db: Session,
    alert_type: str,
    severity: str,
    road_id: int,
    message: str,
):
    road = (
        db.query(Road)
        .filter(Road.id == road_id)
        .first()
    )

    if not road:
        return None

    alert = Alert(
        type=alert_type,
        severity=severity,
        road_id=road_id,
        message=message,
        status="active",
    )

    db.add(alert)
    db.flush()

    _create_recipients(db, alert)

    db.commit()
    db.refresh(alert)

    return alert


def create_delay_alert(
    db: Session,
    road_id: int,
):
    try:
        delay_result = prediction_service.estimate_delay(
            db=db,
            road_id=road_id,
        )
    except ValueError:
        return None

    delay_minutes = delay_result["estimated_delay_minutes"]

    if delay_minutes <= 0:
        return None

    severity = (
        "high"
        if delay_minutes >= 8
        else "medium"
    )

    return create_alert(
        db=db,
        alert_type="delay",
        severity=severity,
        road_id=road_id,
        message=(
            f"Estimated traffic delay of "
            f"{delay_minutes} minutes on Road {road_id}"
        ),
    )


def create_closure_alert(
    db: Session,
    road_id: int,
):
    try:
        condition = get_road_condition(
            db=db,
            road_id=road_id,
        )
    except ValueError:
        return None

    normalized_status = condition["status"].strip().lower()

    closure_statuses = {
        "closed",
        "blocked",
        "road_closed",
    }

    if normalized_status not in closure_statuses:
        return None

    return create_alert(
        db=db,
        alert_type="road_closure",
        severity="high",
        road_id=road_id,
        message=(
            f"Road {road_id} is closed. "
            f"{condition['notes'] or ''}".strip()
        ),
    )


def get_my_alerts(
    db: Session,
    user_id: int,
):
    rows = (
        db.query(Alert, AlertRecipient.read)
        .join(
            AlertRecipient,
            AlertRecipient.alert_id == Alert.id,
        )
        .filter(
            AlertRecipient.user_id == user_id,
        )
        .order_by(Alert.created_at.desc())
        .all()
    )

    return [
        {
            "alert_id": alert.id,
            "type": alert.type,
            "severity": alert.severity,
            "road_id": alert.road_id,
            "message": alert.message,
            "read": read,
            "created_at": alert.created_at,
        }
        for alert, read in rows
    ]


def mark_alert_as_read(
    db: Session,
    alert_id: int,
    user_id: int,
):
    recipient = (
        db.query(AlertRecipient)
        .filter(
            AlertRecipient.alert_id == alert_id,
            AlertRecipient.user_id == user_id,
        )
        .first()
    )

    if not recipient:
        return None

    recipient.read = True

    db.commit()

    return recipient


def get_active_alerts(
    db: Session,
):
    return (
        db.query(Alert)
        .filter(Alert.status == "active")
        .order_by(Alert.created_at.desc())
        .all()
    )
