"""
TrafficVision AI — Alert Service STUB (Milestone 3, Day 2)
Normally owned by: Intern 1 (Team Lead / Backend & Integration)
This version: built by Intern 2 to test the threshold-breach feed
              end-to-end, since I'm working solo.

Purpose:
    A minimal stand-in for Intern 1's real Alert Service, implementing
    just enough of the documented contract (SRS Section 7.1) to prove
    my threshold-monitoring feed actually works:

        POST /api/v1/alerts        <- what my feed calls
        GET  /api/v1/alerts/active <- to verify alerts landed

    This is the SAME PATTERN as the minimal Gateway I built in
    Milestone 2, Day 5 to prove Gateway integration solo — a small,
    honest stub that matches the real contract shape, clearly labeled
    as temporary.

Requirements:
    pip install fastapi uvicorn

Run (in its own terminal, separate from main.py):
    uvicorn alert_service_stub:app --reload --port 8100
"""

from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Alert Service (STUB — normally owned by Intern 1)",
    description="Minimal stand-in implementing just POST /alerts and GET /alerts/active, "
                 "so Intern 2's threshold feed can be tested end-to-end solo.",
)

# In-memory storage only — a real Alert Service would use its own
# database table. This stub exists purely to receive and display
# what my feed sends, not to be a production alert store.
_alerts = []
_next_id = 1


class AlertIn(BaseModel):
    type: str
    severity: str
    road_id: int
    message: str


@app.post("/api/v1/alerts", status_code=201)
def create_alert(alert: AlertIn):
    global _next_id
    record = {
        "alert_id": _next_id,
        "type": alert.type,
        "severity": alert.severity,
        "road_id": alert.road_id,
        "message": alert.message,
        "read": False,
        "created_at": datetime.now().isoformat(),
    }
    _alerts.append(record)
    _next_id += 1
    print(f"[ALERT STUB] New alert created: {record}")
    return {"alert_id": record["alert_id"]}


@app.get("/api/v1/alerts/active")
def get_active_alerts():
    return _alerts


@app.get("/")
def root():
    return {
        "service": "Alert Service STUB",
        "note": "Temporary stand-in for Intern 1's real Alert Service — used to test Intern 2's threshold feed.",
        "alerts_received": len(_alerts),
    }
