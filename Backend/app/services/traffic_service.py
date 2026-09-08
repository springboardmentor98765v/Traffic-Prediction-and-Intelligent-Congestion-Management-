import csv
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from app.config import get_settings

settings = get_settings()

ROAD_NAMES = {
    "R001": "MG Road",
    "R002": "Ring Road",
    "R003": "Station Road",
    "R004": "Airport Road",
    "R005": "Civil Lines",
}

# In-memory cache fallback: { key: (data, expiry_timestamp) }
_in_memory_cache: Dict[str, tuple[Any, float]] = {}

_redis_client = None
_redis_checked = False


def _get_redis_client():
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    try:
        import redis
        client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1)
        client.ping()
        _redis_client = client
    except Exception:
        _redis_client = None
    _redis_checked = True
    return _redis_client


def get_cached(key: str) -> Optional[Any]:
    client = _get_redis_client()
    if client:
        try:
            val = client.get(key)
            if val:
                return json.loads(val)
        except Exception:
            pass
    # Fallback to in-memory cache
    if key in _in_memory_cache:
        data, expiry = _in_memory_cache[key]
        if time.time() < expiry:
            return data
        else:
            del _in_memory_cache[key]
    return None


def set_cached(key: str, data: Any, expiry_seconds: int = 60) -> None:
    client = _get_redis_client()
    if client:
        try:
            client.setex(key, expiry_seconds, json.dumps(data))
            return
        except Exception:
            pass
    _in_memory_cache[key] = (data, time.time() + expiry_seconds)


def _find_csv_path() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "processed_traffic.csv",
        Path(__file__).resolve().parent.parent.parent.parent / "Komal_Data-Engineering-Traffic-Monitoring" / "processed_traffic.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def load_traffic_records() -> List[Dict[str, Any]]:
    csv_path = _find_csv_path()
    if not csv_path.exists():
        now_str = datetime.utcnow().isoformat()
        return [
            {"road_id": rid, "name": name, "vehicle_count": 50, "density": 35.0, "congestion_level": "Medium", "updated_at": now_str}
            for rid, name in ROAD_NAMES.items()
        ]

    records = []
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def calculate_congestion_level(density: float) -> str:
    if density < 20.0:
        return "Low"
    elif density <= 50.0:
        return "Medium"
    else:
        return "High"


def get_live_traffic_data() -> List[Dict[str, Any]]:
    cache_key = "traffic:live"
    cached = get_cached(cache_key)
    if cached:
        return cached

    records = load_traffic_records()
    latest_per_road: Dict[str, Dict[str, Any]] = {}

    for row in records:
        rid = row.get("road_id", "").upper()
        if rid in ROAD_NAMES:
            latest_per_road[rid] = row

    result = []
    now_iso = datetime.utcnow().isoformat()
    for rid, name in ROAD_NAMES.items():
        row = latest_per_road.get(rid)
        if row:
            density = float(row.get("density", 25.0))
            vehicle_count = int(float(row.get("vehicle_count", 30)))
            congestion = row.get("congestion") or calculate_congestion_level(density)
            updated_at = row.get("timestamp") or now_iso
        else:
            density = 25.0
            vehicle_count = 40
            congestion = "Medium"
            updated_at = now_iso

        result.append({
            "road_id": rid,
            "name": name,
            "vehicle_count": vehicle_count,
            "density": round(density, 2),
            "congestion_level": congestion,
            "updated_at": updated_at,
        })

    set_cached(cache_key, result, expiry_seconds=30)
    return result


def get_road_detail(road_id: str) -> Optional[Dict[str, Any]]:
    normalized_id = road_id.upper()
    if normalized_id not in ROAD_NAMES:
        return None

    name = ROAD_NAMES[normalized_id]
    records = load_traffic_records()
    road_records = [r for r in records if r.get("road_id", "").upper() == normalized_id]

    if not road_records:
        latest_density = 25.0
        latest_vehicle_count = 35
        latest_level = "Medium"
        history = []
    else:
        last = road_records[-1]
        latest_density = float(last.get("density", 25.0))
        latest_vehicle_count = int(float(last.get("vehicle_count", 35)))
        latest_level = last.get("congestion") or calculate_congestion_level(latest_density)

        history = []
        for i, rec in enumerate(road_records[-24:]):
            d = float(rec.get("density", 20.0))
            history.append({
                "hour": i,
                "density": round(d, 2),
                "congestion_level": rec.get("congestion") or calculate_congestion_level(d),
                "avg_speed": float(rec.get("avg_speed", 40.0)),
                "timestamp": rec.get("timestamp", ""),
            })

    return {
        "road_id": normalized_id,
        "name": name,
        "congestion_level": latest_level,
        "vehicle_count": latest_vehicle_count,
        "density": round(latest_density, 2),
        "history": history,
    }


def get_density_summary() -> Dict[str, Any]:
    cache_key = "traffic:density_metrics"
    cached = get_cached(cache_key)
    if cached:
        return cached

    live_roads = get_live_traffic_data()
    if not live_roads:
        return {
            "average_density": 0.0,
            "total_roads": 0,
            "congested_roads": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    total_density = sum(r["density"] for r in live_roads)
    congested_count = sum(1 for r in live_roads if r["congestion_level"] == "High")
    avg_density = round(total_density / len(live_roads), 2)

    summary = {
        "average_density": avg_density,
        "total_roads": len(live_roads),
        "congested_roads": congested_count,
        "timestamp": datetime.utcnow().isoformat(),
    }
    set_cached(cache_key, summary, expiry_seconds=30)
    return summary
