from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

@router.post("", response_model=dict, status_code=201)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    """Internal endpoint: called by threshold/anomaly feeds to create an alert."""
    db_alert = models.Alert(
        type=alert.type,
        severity=alert.severity,
        road_id=alert.road_id,
        message=alert.message
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return {"alert_id": db_alert.alert_id}

@router.get("/my", response_model=List[schemas.AlertResponse])
def get_my_alerts(
    x_user_id: str = Header(default=None),
    x_user_role: str = Header(default="commuter"),
    db: Session = Depends(get_db)
):
    """Get alerts applicable to the user, applying RBAC visibility rules."""
    query = db.query(models.Alert)
    
    if x_user_role not in ["admin", "traffic_operator"]:
        # Public (commuter/planner) sees only public-safety alerts
        # Assuming accident and closure are public safety
        query = query.filter(models.Alert.type.in_(["accident", "closure", "delay"]))
        
    # Optional: If user_id is explicitly targeted, handle it. 
    # But mostly alerts are broadcasted based on role.
    
    return query.order_by(models.Alert.created_at.desc()).all()

@router.post("/{alert_id}/read", response_model=schemas.AlertReadResponse)
def mark_alert_read(
    alert_id: int, 
    x_user_id: str = Header(default=None),
    db: Session = Depends(get_db)
):
    """Mark an alert as read. Simple implementation for now."""
    alert = db.query(models.Alert).filter(models.Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.read = True
    db.commit()
    return {"alert_id": alert_id, "read": True}

@router.get("/active", response_model=List[schemas.AlertResponse])
def get_active_alerts(
    x_user_role: str = Header(default="commuter"),
    db: Session = Depends(get_db)
):
    """For Admin/Operator dashboards."""
    if x_user_role not in ["admin", "traffic_operator", "city_planner"]:
        raise HTTPException(status_code=403, detail="Active alerts dashboard is restricted to admin/operator roles.")

    # All unread / active alerts
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()
