import asyncio
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Dict, Any, Set
from fastapi import WebSocket, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from app.models.alert import Alert, AlertRead, AlertType, AlertSeverity
from app.models.user import User, UserRole
from app.models.road_condition import RoadCondition, RoadStatus
from app.schemas.alert import AlertCreate
from app.services import traffic_service

logger = logging.getLogger("alert_service")


# -------------------------------------------------------------------------
# WebSocket Connection Manager for Near-Real-Time Alert Push
# -------------------------------------------------------------------------
class NotificationConnectionManager:
    """Manages active WebSocket connections for live alert broadcasting."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast an alert message to all connected clients."""
        dead_connections = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead_connections.add(connection)
        for dead in dead_connections:
            self.active_connections.discard(dead)


ws_manager = NotificationConnectionManager()


def _broadcast_alert_sync(alert_payload: Dict[str, Any]):
    """Helper to safely dispatch async broadcast from sync context if an event loop is running."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(ws_manager.broadcast({
                "event": "new_alert",
                "alert": alert_payload
            }))
    except Exception:
        pass


# -------------------------------------------------------------------------
# Core Alert Management Operations
# -------------------------------------------------------------------------
def create_alert(
    db: Session,
    alert_in: AlertCreate,
    deduplicate_window_minutes: int = 15
) -> Alert:
    """
    Create a new alert with rate-limiting & deduplication to mitigate alert noise.
    If an active alert of the same type and road exists within the time window,
    update its message and timestamp instead of creating duplicate records.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=deduplicate_window_minutes)

    existing = db.query(Alert).filter(
        Alert.road_id.ilike(alert_in.road_id.strip()),
        Alert.type.ilike(alert_in.type.strip()),
        Alert.is_active == True,
        Alert.created_at >= cutoff
    ).first()

    if existing:
        # Update existing alert to prevent noisy spam
        existing.message = alert_in.message
        existing.updated_at = datetime.utcnow()
        if alert_in.severity.lower() in [AlertSeverity.HIGH.value, AlertSeverity.CRITICAL.value]:
            existing.severity = alert_in.severity.lower()
        db.commit()
        db.refresh(existing)
        return existing

    new_alert = Alert(
        type=alert_in.type.lower(),
        severity=alert_in.severity.lower(),
        road_id=alert_in.road_id.strip().upper(),
        message=alert_in.message,
        target_role=(alert_in.target_role or "public").lower(),
        is_active=True,
        is_read=False,
        source=alert_in.source or "system",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    # Broadcast via WebSocket
    alert_dict = {
        "alert_id": new_alert.id,
        "type": new_alert.type,
        "severity": new_alert.severity,
        "road_id": new_alert.road_id,
        "message": new_alert.message,
        "target_role": new_alert.target_role,
        "created_at": new_alert.created_at.isoformat()
    }
    _broadcast_alert_sync(alert_dict)

    return new_alert


def get_my_alerts(
    db: Session,
    user: Optional[User] = None,
    unread_only: bool = False,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Retrieve alerts scoped to the requesting user's role.
    - Admin/Operator: See all alerts (internal, operational, public).
    - Public/Guest: See public safety alerts (accidents, closures, critical delays, severe congestion).
    Computes per-user read status via AlertRead table.
    """
    query = db.query(Alert).filter(Alert.is_active == True)

    is_privileged = user is not None and user.role.lower() in [UserRole.admin.value, UserRole.operator.value]

    if not is_privileged:
        # Public users only see alerts marked for public or public-safety types
        query = query.filter(
            or_(
                Alert.target_role.ilike("public"),
                Alert.target_role.ilike("all"),
                Alert.type.in_([
                    AlertType.ACCIDENT.value,
                    AlertType.CLOSURE.value,
                    AlertType.DELAY.value
                ])
            )
        )

    alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()

    # Determine read status per user
    read_alert_ids = set()
    if user is not None:
        user_reads = db.query(AlertRead.alert_id).filter(AlertRead.user_id == user.id).all()
        read_alert_ids = {r[0] for r in user_reads}

    results = []
    for a in alerts:
        # If user is logged in, use their personal read history; otherwise check alert's fallback read flag
        is_read = (a.id in read_alert_ids) if user is not None else a.is_read
        if unread_only and is_read:
            continue

        results.append({
            "alert_id": a.id,
            "type": a.type,
            "severity": a.severity,
            "road_id": a.road_id,
            "message": a.message,
            "read": is_read,
            "created_at": a.created_at,
            "is_active": a.is_active,
            "target_role": a.target_role,
            "source": a.source
        })

    return results


def mark_alert_read(
    db: Session,
    alert_id: str,
    user: Optional[User] = None
) -> Dict[str, Any]:
    """
    Mark an alert as read. If a user is authenticated, records entry in AlertRead.
    Also updates the alert's is_read flag.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found"
        )

    if user is not None:
        existing_read = db.query(AlertRead).filter(
            AlertRead.alert_id == alert_id,
            AlertRead.user_id == user.id
        ).first()

        if not existing_read:
            read_record = AlertRead(
                alert_id=alert_id,
                user_id=user.id,
                read_at=datetime.utcnow()
            )
            db.add(read_record)

    alert.is_read = True
    db.commit()

    return {
        "alert_id": alert_id,
        "read": True,
        "message": "Alert marked as read successfully"
    }


def get_active_alerts(
    db: Session,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieve all currently active alerts for Admin/Operator dashboards."""
    alerts = db.query(Alert).filter(
        Alert.is_active == True
    ).order_by(desc(Alert.created_at)).limit(limit).all()

    return [
        {
            "alert_id": a.id,
            "type": a.type,
            "severity": a.severity,
            "road_id": a.road_id,
            "message": a.message,
            "read": a.is_read,
            "created_at": a.created_at,
            "is_active": a.is_active,
            "target_role": a.target_role,
            "source": a.source
        }
        for a in alerts
    ]


def poll_alerts(
    db: Session,
    user: Optional[User] = None,
    since: Optional[datetime] = None,
    unread_only: bool = False,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Near-real-time short-interval REST polling endpoint.
    Returns alerts, unread counts, and active counts since the specified timestamp.
    """
    all_my = get_my_alerts(db, user=user, unread_only=False, limit=limit)

    unread_count = sum(1 for a in all_my if not a["read"])
    active_count = len(all_my)

    if since:
        # Filter for items created or updated after 'since'
        filtered = [
            a for a in all_my
            if a["created_at"] > since
        ]
    else:
        filtered = all_my

    if unread_only:
        filtered = [a for a in filtered if not a["read"]]

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "unread_count": unread_count,
        "active_count": active_count,
        "alerts": filtered[:limit]
    }


# -------------------------------------------------------------------------
# Automated Trigger Feeds (FR-01, FR-02, FR-03)
# -------------------------------------------------------------------------
def trigger_congestion_alerts_from_telemetry(
    db: Session,
    density_threshold: float = 60.0
) -> List[Alert]:
    """
    FR-01: Detect congestion-threshold breaches on monitored roads and generate congestion alerts.
    """
    live_records = traffic_service.get_live_traffic_data()
    generated_alerts = []

    for item in live_records:
        rid = item.get("road_id")
        name = item.get("name", rid)
        density = float(item.get("density", 0.0))
        congestion_level = item.get("congestion_level", "Low")
        vehicle_count = item.get("vehicle_count", 0)

        # Trigger if density crosses threshold or congestion level is High
        if density >= density_threshold or congestion_level.lower() == "high":
            severity = AlertSeverity.CRITICAL.value if density > 80.0 else AlertSeverity.HIGH.value
            alert_in = AlertCreate(
                type=AlertType.CONGESTION.value,
                severity=severity,
                road_id=rid,
                message=f"High Congestion Alert: {name} ({rid}) density has reached {density:.1f}% with {vehicle_count} vehicles detected.",
                target_role="public",
                source="threshold_feed"
            )
            created = create_alert(db, alert_in, deduplicate_window_minutes=15)
            generated_alerts.append(created)

    return generated_alerts


def trigger_road_closure_and_delay_alerts(db: Session) -> List[Alert]:
    """
    FR-03: Generate road-closure and delay notifications sourced from monitoring & route data.
    """
    conditions = db.query(RoadCondition).all()
    generated_alerts = []

    for cond in conditions:
        rid = cond.road_id
        name = cond.road_name or rid
        status_val = (cond.status or "").upper()

        if status_val == RoadStatus.CLOSED.value:
            alert_in = AlertCreate(
                type=AlertType.CLOSURE.value,
                severity=AlertSeverity.CRITICAL.value,
                road_id=rid,
                message=f"ROAD CLOSURE: {name} ({rid}) is CLOSED to traffic. Note: {cond.notes}",
                target_role="public",
                source="road_condition"
            )
            created = create_alert(db, alert_in, deduplicate_window_minutes=20)
            generated_alerts.append(created)

        elif status_val in [RoadStatus.HAZARD.value, RoadStatus.CONSTRUCTION.value]:
            alert_in = AlertCreate(
                type=AlertType.DELAY.value,
                severity=AlertSeverity.HIGH.value if status_val == RoadStatus.HAZARD.value else AlertSeverity.MEDIUM.value,
                road_id=rid,
                message=f"Traffic Delay Warning: {name} ({rid}) reports {status_val.lower()} conditions. Note: {cond.notes}",
                target_role="public",
                source="road_condition"
            )
            created = create_alert(db, alert_in, deduplicate_window_minutes=20)
            generated_alerts.append(created)

    return generated_alerts


def trigger_accident_alerts_from_anomalies(
    db: Session,
    anomalies: List[Dict[str, Any]]
) -> List[Alert]:
    """
    FR-02: Detect anomalous traffic patterns and generate accident alerts.
    """
    generated_alerts = []
    for anom in anomalies:
        rid = anom.get("road_id")
        expected = anom.get("expected_level", "Low")
        observed = anom.get("observed_level", "High")
        flagged = anom.get("flagged_as", "possible_incident")

        if flagged == "possible_incident":
            severity = anom.get("severity", AlertSeverity.CRITICAL.value)
            alert_in = AlertCreate(
                type=AlertType.ACCIDENT.value,
                severity=severity,
                road_id=rid,
                message=f"ACCIDENT / INCIDENT ALERT: Unusual traffic pattern flagged on {rid}. Expected congestion was '{expected}', but observed level is '{observed}'. Potential collision or lane blockage.",
                target_role="public",
                source="anomaly_detector"
            )
            created = create_alert(db, alert_in, deduplicate_window_minutes=15)
            generated_alerts.append(created)

    return generated_alerts


def evaluate_all_triggers(db: Session) -> Dict[str, Any]:
    """
    Evaluate all alert trigger feeds (congestion threshold, road closures, delays)
    and return summary.
    """
    congestion_alerts = trigger_congestion_alerts_from_telemetry(db)
    condition_alerts = trigger_road_closure_and_delay_alerts(db)

    total_triggered = len(congestion_alerts) + len(condition_alerts)
    return {
        "status": "success",
        "total_triggered": total_triggered,
        "congestion_alerts_count": len(congestion_alerts),
        "condition_alerts_count": len(condition_alerts),
        "alerts": [
            {
                "alert_id": a.id,
                "type": a.type,
                "severity": a.severity,
                "road_id": a.road_id,
                "message": a.message,
                "created_at": a.created_at,
                "status": "created"
            }
            for a in (congestion_alerts + condition_alerts)
        ]
    }
