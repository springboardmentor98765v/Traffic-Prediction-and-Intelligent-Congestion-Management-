from datetime import date, datetime, time
from zoneinfo import ZoneInfo
from app.database import engine

IST = ZoneInfo("Asia/Kolkata")


def _format_timestamp(value):
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            value = value.replace(tzinfo=IST)
        return value.isoformat()
    if isinstance(value, str):
        try:
            return _format_timestamp(datetime.fromisoformat(value.replace("Z", "+00:00")))
        except ValueError:
            return value
    return str(value)


def get_postgres_connection():
    try:
        return engine.raw_connection()
    except Exception:
        return None


# Safe fallback sample data
SAMPLE_FALLBACK_DATA = [
    {
        "road_id": "R001",
        "vehicle_count": 28,
        "density": 5.6,
        "congestion_level": "Low",
        "reading_timestamp": "2026-08-26T22:00:00",
    },
    {
        "road_id": "R002",
        "vehicle_count": 27,
        "density": 6.75,
        "congestion_level": "Low",
        "reading_timestamp": "2026-08-26T22:00:00",
    },
    {
        "road_id": "R003",
        "vehicle_count": 26,
        "density": 7.43,
        "congestion_level": "Low",
        "reading_timestamp": "2026-08-26T22:00:00",
    },
    {
        "road_id": "R004",
        "vehicle_count": 1,
        "density": 0.22,
        "congestion_level": "Low",
        "reading_timestamp": "2026-08-26T22:00:00",
    },
    {
        "road_id": "R005",
        "vehicle_count": 34,
        "density": 11.33,
        "congestion_level": "Medium",
        "reading_timestamp": "2026-08-26T22:00:00",
    },
    {
        "road_id": "R006",
        "vehicle_count": 55,
        "density": 22.4,
        "congestion_level": "High",
        "reading_timestamp": "2026-08-26T22:00:00",
    },
]


def _parse_timestamp(value, field_name):
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, time.min)
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=IST)
    return parsed


def _validate_time_window(start_time, end_time):
    start = _parse_timestamp(start_time, "start_time")
    end = _parse_timestamp(end_time, "end_time")
    if start is not None and end is not None and start > end:
        raise ValueError("start_time must not be after end_time")
    return start, end


def _filter_fallback_history(road_id, start_time, end_time, limit):
    start, end = _validate_time_window(start_time, end_time)
    rows = SAMPLE_FALLBACK_DATA
    if road_id:
        rows = [row for row in rows if row["road_id"].upper() == road_id.upper()]

    filtered = []
    for row in rows:
        stamp_value = row.get("reading_timestamp") or row.get("updated_at")
        stamp = _parse_timestamp(stamp_value, "reading_timestamp")
        if start is not None and stamp < start:
            continue
        if end is not None and stamp > end:
            continue
        formatted = dict(row)
        formatted["reading_timestamp"] = _format_timestamp(stamp)
        formatted["updated_at"] = _format_timestamp(stamp)
        filtered.append(formatted)
    return filtered[:limit]


def _fallback_live_traffic():
    return [
        {
            **row,
            "updated_at": _format_timestamp(row["reading_timestamp"]),
        }
        for row in SAMPLE_FALLBACK_DATA
    ]


def get_live_traffic():
    conn = get_postgres_connection()
    if not conn:
        return _fallback_live_traffic()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT ON (tr.road_id)
                    tr.road_id,
                    tr.vehicle_count,
                    tr.traffic_density_vehicles_per_km,
                    tr.congestion_level,
                    tr.reading_timestamp
                FROM traffic_readings tr
                ORDER BY tr.road_id, tr.reading_timestamp DESC, tr.reading_id DESC;
            """)
            rows = cursor.fetchall()
            return [
                {
                    "road_id": r[0],
                    "vehicle_count": r[1],
                    "density": float(r[2]),
                    "congestion_level": r[3],
                    "updated_at": _format_timestamp(r[4]),
                }
                for r in rows
            ]
    except Exception:
        return _fallback_live_traffic()
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_road_traffic(road_id):
    conn = get_postgres_connection()
    if not conn:
        for item in SAMPLE_FALLBACK_DATA:
            if item["road_id"].upper() == road_id.upper():
                sample = {
                    **item,
                    "updated_at": _format_timestamp(item["reading_timestamp"]),
                }
                return {
                    "road_id": item["road_id"],
                    "name": f"Road {item['road_id']}",
                    "congestion_level": item["congestion_level"],
                    "history": [sample],
                }
        return None

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT vehicle_count, traffic_density_vehicles_per_km, congestion_level,
                       reading_timestamp, avg_speed_kmph
                FROM traffic_readings WHERE road_id = %s ORDER BY reading_timestamp DESC;
            """,
                (road_id,),
            )
            rows = cursor.fetchall()
            if not rows:
                return None
            history = [
                {
                    "vehicle_count": r[0],
                    "density": float(r[1]),
                    "congestion_level": r[2],
                    "avg_speed_kmph": float(r[4]) if r[4] is not None else None,
                    "updated_at": _format_timestamp(r[3]),
                }
                for r in rows
            ]
            return {
                "road_id": road_id,
                "name": f"Road {road_id}",
                "congestion_level": rows[0][2],
                "history": history,
            }
    except Exception:
        for item in SAMPLE_FALLBACK_DATA:
            if item["road_id"].upper() == road_id.upper():
                return {
                    "road_id": item["road_id"],
                    "name": f"Road {item['road_id']}",
                    "congestion_level": item["congestion_level"],
                    "history": [item],
                }
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_density_summary():
    conn = get_postgres_connection()
    if not conn:
        return {
            "total_roads": len(SAMPLE_FALLBACK_DATA),
            "average_density": 7.3,
            "maximum_density": 22.4,
            "minimum_density": 0.22,
            "high_congestion_roads": 1,
            "severe_congestion_roads": 0,
            "total_vehicle_count": sum(i["vehicle_count"] for i in SAMPLE_FALLBACK_DATA),
        }

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                WITH latest AS (
                    SELECT DISTINCT ON (road_id) road_id, traffic_density_vehicles_per_km,
                           congestion_level, vehicle_count
                    FROM traffic_readings ORDER BY road_id, reading_timestamp DESC
                )
                SELECT COUNT(*),
                       COALESCE(AVG(traffic_density_vehicles_per_km), 0),
                       COALESCE(MAX(traffic_density_vehicles_per_km), 0),
                       COALESCE(MIN(traffic_density_vehicles_per_km), 0),
                       COUNT(*) FILTER (WHERE congestion_level = 'High'),
                       COUNT(*) FILTER (WHERE congestion_level = 'Severe'),
                       COALESCE(SUM(vehicle_count), 0)
                FROM latest;
            """)
            row = cursor.fetchone()
            return {
                "total_roads": row[0],
                "average_density": round(float(row[1]), 2),
                "maximum_density": round(float(row[2]), 2),
                "minimum_density": round(float(row[3]), 2),
                "high_congestion_roads": row[4],
                "severe_congestion_roads": row[5],
                "total_vehicle_count": row[6],
            }
    except Exception:
        return {
            "total_roads": len(SAMPLE_FALLBACK_DATA),
            "average_density": 7.3,
            "maximum_density": 22.4,
            "minimum_density": 0.22,
            "high_congestion_roads": 1,
            "severe_congestion_roads": 0,
            "total_vehicle_count": sum(i["vehicle_count"] for i in SAMPLE_FALLBACK_DATA),
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_traffic_history(road_id=None, start_time=None, end_time=None, limit=500):
    start, end = _validate_time_window(start_time, end_time)
    if not 1 <= limit <= 5000:
        raise ValueError("limit must be between 1 and 5000")

    conn = get_postgres_connection()
    if not conn:
        return _filter_fallback_history(road_id, start_time, end_time, limit)

    try:
        with conn.cursor() as cursor:
            query = (
                "SELECT road_id, vehicle_count, traffic_density_vehicles_per_km, congestion_level,"
                " reading_timestamp FROM traffic_readings WHERE 1=1"
            )
            params = []
            if road_id:
                query += " AND road_id = %s"
                params.append(road_id)
            if start_time:
                query += " AND reading_timestamp >= %s"
                params.append(start_time)
            if end_time:
                query += " AND reading_timestamp <= %s"
                params.append(end_time)
            query += " ORDER BY reading_timestamp DESC LIMIT %s;"
            params.append(limit)
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [
                {
                    "road_id": r[0],
                    "vehicle_count": r[1],
                    "density": float(r[2]),
                    "congestion_level": r[3],
                    "reading_timestamp": _format_timestamp(r[4]),
                }
                for r in rows
            ]
    except Exception:
        return _filter_fallback_history(road_id, start_time, end_time, limit)
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_traffic_aggregate(road_id=None, start_time=None, end_time=None, interval="day"):
    start, end = _validate_time_window(start_time, end_time)
    if interval not in {"hour", "day"}:
        raise ValueError("interval must be 'hour' or 'day'")

    conn = get_postgres_connection()
    if not conn:
        rows = _filter_fallback_history(road_id, start_time, end_time, 5000)
        grouped = {}
        for row in rows:
            stamp = _parse_timestamp(
                row.get("reading_timestamp") or row.get("updated_at"),
                "reading_timestamp",
            )
            period = (
                stamp.replace(minute=0, second=0, microsecond=0)
                if interval == "hour"
                else stamp.replace(hour=0, minute=0, second=0, microsecond=0)
            )
            key = (row["road_id"], period)
            grouped.setdefault(key, []).append(row)
        return [
            {
                "road_id": grouped_rows[0]["road_id"],
                "period_start": period.isoformat(),
                "total_readings": len(grouped_rows),
                "avg_vehicle_count": round(
                    sum(item["vehicle_count"] for item in grouped_rows) / len(grouped_rows), 2
                ),
                "avg_density": round(
                    sum(item["density"] for item in grouped_rows) / len(grouped_rows), 2
                ),
            }
            for (road_id, period), grouped_rows in sorted(grouped.items())
        ]

    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            if road_id:
                conditions.append("road_id = %s")
                params.append(road_id)
            if start_time:
                conditions.append("reading_timestamp >= %s")
                params.append(start_time)
            if end_time:
                conditions.append("reading_timestamp <= %s")
                params.append(end_time)
            where = "WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"""
                SELECT road_id, date_trunc('{interval}', reading_timestamp) AS period_start,
                       AVG(vehicle_count), AVG(traffic_density_vehicles_per_km), COUNT(*)
                FROM traffic_readings
                {where}
                GROUP BY road_id, date_trunc('{interval}', reading_timestamp)
                ORDER BY road_id, period_start;
            """
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [
                {
                    "road_id": row[0],
                    "period_start": (
                        row[1].isoformat() if hasattr(row[1], "isoformat") else str(row[1])
                    ),
                    "avg_vehicle_count": float(row[2]) if row[2] is not None else None,
                    "avg_density": float(row[3]) if row[3] is not None else None,
                    "total_readings": row[4],
                }
                for row in rows
            ]
    except Exception:
        rows = _filter_fallback_history(road_id, start_time, end_time, 5000)
        return [
            {
                "road_id": row["road_id"],
                "period_start": row.get("reading_timestamp") or row.get("updated_at"),
                "avg_vehicle_count": float(row["vehicle_count"]),
                "avg_density": float(row["density"]),
                "total_readings": 1,
            }
            for row in rows
        ]
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_road_condition(road_id: str):
    conn = get_postgres_connection()
    if not conn:
        return {
            "road_id": road_id,
            "road_name": f"Road {road_id}",
            "surface_condition": "Good",
            "status": "Clear",
        }

    try:
        with conn.cursor() as cursor:
            # road_condition / road_status / incident_type / description / source
            # live on the separate road_conditions table, not on roads — join to
            # roads only for the display name, and take the most recent
            # condition row per road_id.
            cursor.execute(
                """
                SELECT r.road_id, r.road_name, rc.road_condition, rc.road_status,
                       rc.incident_type, rc.description, rc.source
                FROM roads r
                LEFT JOIN road_conditions rc ON rc.road_id = r.road_id
                WHERE r.road_id = %s
                ORDER BY rc.condition_timestamp DESC
                LIMIT 1;
            """,
                (road_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "road_id": row[0],
                "road_name": row[1] if row[1] else f"Road {row[0]}",
                "surface_condition": row[2] if row[2] else "Good",
                "status": row[3] if row[3] else "Clear",
                "incident_type": row[4],
                "description": row[5],
                "source": row[6],
            }
    except Exception:
        return {
            "road_id": road_id,
            "road_name": f"Road {road_id}",
            "surface_condition": "Good",
            "status": "Clear",
        }
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_hourly_metrics(road_id=None, start_time=None, end_time=None, limit=500):
    return get_traffic_history(road_id, start_time, end_time, limit)


def get_daily_metrics(road_id=None, start_date=None, end_date=None, limit=500):
    return get_traffic_history(road_id, start_date, end_date, limit)
