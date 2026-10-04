import requests
from sqlalchemy.orm import Session

from app.alerts.service import create_alert
from app.database.models import Alert

SHARMILA_ALERTS_URL = "http://host.docker.internal:8000/analytics/alerts"


def sync_congestion_alerts(db: Session):
    response = requests.get(SHARMILA_ALERTS_URL, timeout=5)
    response.raise_for_status()

    breaches = response.json()

    created = 0
    skipped = 0

    for breach in breaches:
        alert_type = breach.get("alert_type", "congestion")
        severity = "high"
        road_id = int(breach["road_id"])
        message = breach["message"]

        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.type == alert_type,
                Alert.severity == severity,
                Alert.road_id == road_id,
                Alert.message == message,
            )
            .first()
        )

        if existing_alert:
            skipped += 1
            continue

        alert = create_alert(
            db=db,
            alert_type=alert_type,
            severity=severity,
            road_id=road_id,
            message=message,
        )

        if alert:
            created += 1
        else:
            skipped += 1

    return {
        "source": "Sharmila congestion threshold feed",
        "breaches_received": len(breaches),
        "alerts_created": created,
        "alerts_skipped": skipped,
    }



