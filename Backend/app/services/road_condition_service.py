from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# In-memory store initialized with realistic Bangalore corridor conditions
_ROAD_CONDITIONS: Dict[str, Dict[str, Any]] = {
    "R001": {
        "road_id": "R001",
        "road_name": "MG Road",
        "status": "OPEN",
        "notes": "Clear roadway, normal driving conditions",
        "severity": "Low",
        "updated_at": "2026-09-14T08:00:00Z",
        "updated_by": "system"
    },
    "R002": {
        "road_id": "R002",
        "road_name": "Ring Road",
        "status": "OPEN",
        "notes": "High vehicular density during peak hours; all lanes open",
        "severity": "Low",
        "updated_at": "2026-09-14T08:30:00Z",
        "updated_by": "system"
    },
    "R003": {
        "road_id": "R003",
        "road_name": "Station Road",
        "status": "CONSTRUCTION",
        "notes": "Metro feeder construction near south intersection; single lane diversion",
        "severity": "Medium",
        "updated_at": "2026-09-14T06:00:00Z",
        "updated_by": "traffic_police"
    },
    "R004": {
        "road_id": "R004",
        "road_name": "Airport Road",
        "status": "OPEN",
        "notes": "Expressway clear, normal speed limits apply",
        "severity": "Low",
        "updated_at": "2026-09-14T07:15:00Z",
        "updated_by": "system"
    },
    "R005": {
        "road_id": "R005",
        "road_name": "Civil Lines",
        "status": "OPEN",
        "notes": "Administrative zone; smooth traffic flow",
        "severity": "Low",
        "updated_at": "2026-09-14T08:00:00Z",
        "updated_by": "system"
    }
}


def get_road_condition(road_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve road condition record for given road ID."""
    norm_id = road_id.strip().upper()
    return _ROAD_CONDITIONS.get(norm_id)


def get_all_road_conditions() -> List[Dict[str, Any]]:
    """Retrieve all current road condition records."""
    return list(_ROAD_CONDITIONS.values())


def update_road_condition(
    road_id: str,
    status: str,
    notes: Optional[str] = None,
    severity: Optional[str] = "Low",
    updated_by: Optional[str] = "operator"
) -> Dict[str, Any]:
    """Update or insert a road condition flag."""
    norm_id = road_id.strip().upper()
    now_iso = datetime.now(timezone.utc).isoformat()

    existing = _ROAD_CONDITIONS.get(norm_id, {
        "road_id": norm_id,
        "road_name": norm_id,
    })

    record = {
        "road_id": norm_id,
        "road_name": existing.get("road_name", norm_id),
        "status": status.upper(),
        "notes": notes or existing.get("notes", "Status updated"),
        "severity": severity or existing.get("severity", "Low"),
        "updated_at": now_iso,
        "updated_by": updated_by or "operator"
    }
    _ROAD_CONDITIONS[norm_id] = record
    return record
