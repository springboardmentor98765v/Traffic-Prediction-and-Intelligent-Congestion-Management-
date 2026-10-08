import os

from database import get_postgres_connection

from app.redis_cache import (
    get_redis_client,
    get_cached_live_traffic,
    cache_live_traffic,
)

# Cache live traffic for 30 seconds by default
LIVE_CACHE_TTL = int(os.getenv("REDIS_TTL_SECONDS", "30"))


# =========================================================
# DAY 4 - LIVE TRAFFIC WITH REDIS CACHE
# =========================================================


def get_live_traffic():
    """
    Return the latest traffic information for all roads.

    Day 4 workflow:

    1. Check Redis first.
    2. If data exists -> return cached data.
    3. If Redis cache misses -> read PostgreSQL.
    4. Store PostgreSQL result in Redis.
    5. Return traffic data.
    """

    redis_client = get_redis_client()

    try:

        # -------------------------------------------------
        # STEP 1: Check Redis
        # -------------------------------------------------

        try:

            cached_data = get_cached_live_traffic(redis_client)

            if cached_data is not None:

                print("Redis HIT: traffic:live")

                return cached_data

            print("Redis MISS: traffic:live")

        except Exception as redis_error:

            print(f"Redis read error: {redis_error}")

            print("Continuing with PostgreSQL...")

        # -------------------------------------------------
        # STEP 2: Get latest traffic from PostgreSQL
        # -------------------------------------------------

        print("Fetching live traffic from PostgreSQL")

        query = """
            SELECT DISTINCT ON (tr.road_id)
                tr.road_id,
                tr.vehicle_count,
                tr.traffic_density_vehicles_per_km,
                tr.congestion_level,
                tr.reading_timestamp
            FROM traffic_readings tr
            ORDER BY
                tr.road_id,
                tr.reading_timestamp DESC,
                tr.reading_id DESC;
        """

        conn = get_postgres_connection()

        try:

            with conn.cursor() as cursor:

                cursor.execute(query)

                rows = cursor.fetchall()

                result = []

                for row in rows:

                    result.append(
                        {
                            "road_id": row[0],
                            "vehicle_count": row[1],
                            "density": float(row[2]),
                            "congestion_level": row[3],
                            "updated_at": row[4].isoformat(),
                        }
                    )

        finally:

            conn.close()

        # -------------------------------------------------
        # STEP 3: Store result in Redis
        # -------------------------------------------------

        try:

            cache_live_traffic(redis_client, result, LIVE_CACHE_TTL)

            print("Cached traffic:live in Redis")

            print(f"Cache TTL: {LIVE_CACHE_TTL} seconds")

        except Exception as redis_error:

            print(f"Redis write error: {redis_error}")

        # -------------------------------------------------
        # STEP 4: Return result
        # -------------------------------------------------

        return result

    finally:

        redis_client.close()


# =========================================================
# ROAD-SPECIFIC TRAFFIC + CONGESTION HISTORY
# =========================================================


def get_road_traffic(road_id):

    # Get road information
    road_query = """
        SELECT
            road_id,
            road_name
        FROM roads
        WHERE road_id = %s;
    """

    # Get congestion/traffic history
    history_query = """
        SELECT
            vehicle_count,
            traffic_density_vehicles_per_km,
            congestion_level,
            reading_timestamp,
            avg_speed_kmph
        FROM traffic_readings
        WHERE road_id = %s
        ORDER BY
            reading_timestamp DESC,
            reading_id DESC;
    """

    conn = get_postgres_connection()

    try:

        with conn.cursor() as cursor:

            # ---------------------------------------------
            # Find road
            # ---------------------------------------------

            cursor.execute(road_query, (road_id,))

            road = cursor.fetchone()

            if road is None:

                return None

            # ---------------------------------------------
            # Get history
            # ---------------------------------------------

            cursor.execute(history_query, (road_id,))

            rows = cursor.fetchall()

            if not rows:

                return {
                    "road_id": road[0],
                    "name": road[1],
                    "congestion_level": "Unknown",
                    "history": [],
                }

            # Latest reading
            latest = rows[0]

            history = []

            for row in rows:

                history.append(
                    {
                        "vehicle_count": row[0],
                        "density": float(row[1]),
                        "congestion_level": row[2],
                        "avg_speed_kmph": (float(row[4]) if row[4] is not None else None),
                        "updated_at": (row[3].isoformat()),
                    }
                )

            return {
                "road_id": road[0],
                "name": road[1],
                "congestion_level": latest[2],
                "history": history,
            }

    finally:

        conn.close()


# =========================================================
# TRAFFIC DENSITY SUMMARY
# =========================================================


def get_density_summary():

    query = """
        WITH latest_traffic AS (

            SELECT DISTINCT ON (road_id)

                road_id,

                traffic_density_vehicles_per_km,

                congestion_level,

                vehicle_count

            FROM traffic_readings

            ORDER BY
                road_id,
                reading_timestamp DESC,
                reading_id DESC
        )

        SELECT

            COUNT(*) AS total_roads,

            COALESCE(
                AVG(
                    traffic_density_vehicles_per_km
                ),
                0
            ) AS average_density,

            COALESCE(
                MAX(
                    traffic_density_vehicles_per_km
                ),
                0
            ) AS maximum_density,

            COALESCE(
                MIN(
                    traffic_density_vehicles_per_km
                ),
                0
            ) AS minimum_density,

            COUNT(*) FILTER (
                WHERE congestion_level = 'High'
            ) AS high_congestion_roads,

            COUNT(*) FILTER (
                WHERE congestion_level = 'Severe'
            ) AS severe_congestion_roads,

            COALESCE(
                SUM(vehicle_count),
                0
            ) AS total_vehicle_count

        FROM latest_traffic;
    """

    conn = get_postgres_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute(query)

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

    finally:

        conn.close()


# =========================================================
# M2 DAY 3 - HISTORICAL DATA API
# =========================================================


def get_traffic_history(road_id=None, start_time=None, end_time=None, limit=500):
    """Return cleaned historical traffic readings for ML/API consumers."""
    conditions = []
    params = []

    if road_id:
        conditions.append("th.road_id = %s")
        params.append(road_id)
    if start_time:
        conditions.append("th.reading_timestamp >= %s")
        params.append(start_time)
    if end_time:
        conditions.append("th.reading_timestamp <= %s")
        params.append(end_time)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query = f"""
        SELECT
            th.history_id,
            th.road_id,
            th.sensor_id,
            th.reading_timestamp,
            th.vehicle_count,
            th.avg_speed_kmph,
            th.road_capacity,
            th.traffic_density_vehicles_per_km,
            th.congestion_level,
            th.latitude,
            th.longitude,
            th.source
        FROM traffic_history th
        {where_clause}
        ORDER BY th.reading_timestamp ASC, th.history_id ASC
        LIMIT %s;
    """
    params.append(limit)

    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append(
                    {
                        "history_id": row[0],
                        "road_id": row[1],
                        "sensor_id": row[2],
                        "timestamp": row[3].isoformat(),
                        "vehicle_count": row[4],
                        "avg_speed_kmph": float(row[5]) if row[5] is not None else None,
                        "road_capacity": row[6],
                        "traffic_density_vehicles_per_km": float(row[7]),
                        "congestion_level": row[8],
                        "latitude": float(row[9]) if row[9] is not None else None,
                        "longitude": float(row[10]) if row[10] is not None else None,
                        "source": row[11],
                    }
                )
            return {"count": len(data), "data": data}
    finally:
        conn.close()


def get_traffic_aggregate(road_id=None, start_time=None, end_time=None, interval="day"):
    """Return aggregate historical traffic metrics grouped by hour or day."""
    if interval not in {"hour", "day"}:
        raise ValueError("interval must be 'hour' or 'day'")

    conditions = []
    params = []
    if road_id:
        conditions.append("th.road_id = %s")
        params.append(road_id)
    if start_time:
        conditions.append("th.reading_timestamp >= %s")
        params.append(start_time)
    if end_time:
        conditions.append("th.reading_timestamp <= %s")
        params.append(end_time)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    bucket = "day" if interval == "day" else "hour"

    query = f"""
        SELECT
            th.road_id,
            date_trunc('{bucket}', th.reading_timestamp) AS period_start,
            COUNT(*) AS total_readings,
            ROUND(AVG(th.vehicle_count)::numeric, 2) AS avg_vehicle_count,
            MAX(th.vehicle_count) AS max_vehicle_count,
            ROUND(AVG(th.avg_speed_kmph)::numeric, 2) AS avg_speed_kmph,
            ROUND(MIN(th.avg_speed_kmph)::numeric, 2) AS min_speed_kmph,
            ROUND(AVG(th.traffic_density_vehicles_per_km)::numeric, 2) AS avg_density,
            ROUND(MAX(th.traffic_density_vehicles_per_km)::numeric, 2) AS max_density,
            COUNT(*) FILTER (WHERE th.congestion_level = 'High') AS high_congestion_count,
            COUNT(*) FILTER (WHERE th.congestion_level = 'Severe') AS severe_congestion_count
        FROM traffic_history th
        {where_clause}
        GROUP BY th.road_id, date_trunc('{bucket}', th.reading_timestamp)
        ORDER BY th.road_id, period_start;
    """

    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            data = []
            for row in rows:
                data.append(
                    {
                        "road_id": row[0],
                        "period_start": row[1].isoformat(),
                        "total_readings": row[2],
                        "avg_vehicle_count": float(row[3]) if row[3] is not None else None,
                        "max_vehicle_count": row[4],
                        "avg_speed_kmph": float(row[5]) if row[5] is not None else None,
                        "min_speed_kmph": float(row[6]) if row[6] is not None else None,
                        "avg_density": float(row[7]) if row[7] is not None else None,
                        "max_density": float(row[8]) if row[8] is not None else None,
                        "high_congestion_count": row[9],
                        "severe_congestion_count": row[10],
                    }
                )
            return {"interval": interval, "count": len(data), "data": data}
    finally:
        conn.close()


# =========================================================
# M2 DAY 4 - ROAD CONDITIONS
# =========================================================


def get_road_condition(road_id):
    """Return road-condition records for a specific road."""
    road_query = """
        SELECT road_id, road_name
        FROM roads
        WHERE road_id = %s;
    """

    condition_query = """
        SELECT
            condition_id,
            road_id,
            condition_timestamp,
            road_condition,
            road_status,
            incident_type,
            description,
            source,
            created_at
        FROM road_conditions
        WHERE road_id = %s
        ORDER BY condition_timestamp DESC, condition_id DESC;
    """

    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(road_query, (road_id,))
            road = cursor.fetchone()

            if road is None:
                return None

            cursor.execute(condition_query, (road_id,))
            rows = cursor.fetchall()

            conditions = []
            for row in rows:
                conditions.append(
                    {
                        "condition_id": row[0],
                        "road_id": row[1],
                        "condition_timestamp": row[2].isoformat(),
                        "road_condition": row[3],
                        "road_status": row[4],
                        "incident_type": row[5],
                        "description": row[6],
                        "source": row[7],
                        "created_at": row[8].isoformat(),
                    }
                )

            return {
                "road_id": road[0],
                "road_name": road[1],
                "count": len(conditions),
                "conditions": conditions,
            }
    finally:
        conn.close()


# =========================================================
# M2 DAY 5 - PRE-AGGREGATED HOURLY METRICS
# =========================================================


def get_hourly_metrics(road_id=None, start_time=None, end_time=None, limit=500):
    """
    Return pre-aggregated hourly traffic metrics.
    """

    query = """
        SELECT
            road_id,
            metric_timestamp,
            avg_vehicle_count,
            max_vehicle_count,
            avg_speed_kmph,
            min_speed_kmph,
            avg_density,
            max_density,
            total_readings,
            high_congestion_count,
            severe_congestion_count,
            high_congestion_percentage,
            severe_congestion_percentage
        FROM hourly_traffic_metrics
        WHERE 1 = 1
    """

    params = []

    if road_id:
        query += " AND road_id = %s"
        params.append(road_id)

    if start_time:
        query += " AND metric_timestamp >= %s"
        params.append(start_time)

    if end_time:
        query += " AND metric_timestamp <= %s"
        params.append(end_time)

    query += """
        ORDER BY metric_timestamp DESC, road_id
        LIMIT %s
    """

    params.append(limit)

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            data = []

            for row in rows:
                data.append(
                    {
                        "road_id": row[0],
                        "metric_timestamp": row[1].isoformat(),
                        "avg_vehicle_count": (float(row[2]) if row[2] is not None else None),
                        "max_vehicle_count": row[3],
                        "avg_speed_kmph": (float(row[4]) if row[4] is not None else None),
                        "min_speed_kmph": (float(row[5]) if row[5] is not None else None),
                        "avg_density": (float(row[6]) if row[6] is not None else None),
                        "max_density": (float(row[7]) if row[7] is not None else None),
                        "total_readings": row[8],
                        "high_congestion_count": row[9],
                        "severe_congestion_count": row[10],
                        "high_congestion_percentage": (
                            float(row[11]) if row[11] is not None else None
                        ),
                        "severe_congestion_percentage": (
                            float(row[12]) if row[12] is not None else None
                        ),
                    }
                )

            return {"interval": "hour", "count": len(data), "data": data}

    finally:
        conn.close()


# =========================================================
# M2 DAY 5 - PRE-AGGREGATED DAILY METRICS
# =========================================================


def get_daily_metrics(road_id=None, start_date=None, end_date=None, limit=500):
    """
    Return pre-aggregated daily traffic metrics.
    """

    query = """
        SELECT
            road_id,
            metric_date,
            avg_vehicle_count,
            max_vehicle_count,
            avg_speed_kmph,
            min_speed_kmph,
            avg_density,
            max_density,
            total_readings,
            high_congestion_count,
            severe_congestion_count,
            high_congestion_percentage,
            severe_congestion_percentage
        FROM daily_traffic_metrics
        WHERE 1 = 1
    """

    params = []

    if road_id:
        query += " AND road_id = %s"
        params.append(road_id)

    if start_date:
        query += " AND metric_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND metric_date <= %s"
        params.append(end_date)

    query += """
        ORDER BY metric_date DESC, road_id
        LIMIT %s
    """

    params.append(limit)

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            data = []

            for row in rows:
                data.append(
                    {
                        "road_id": row[0],
                        "metric_date": row[1].isoformat(),
                        "avg_vehicle_count": (float(row[2]) if row[2] is not None else None),
                        "max_vehicle_count": row[3],
                        "avg_speed_kmph": (float(row[4]) if row[4] is not None else None),
                        "min_speed_kmph": (float(row[5]) if row[5] is not None else None),
                        "avg_density": (float(row[6]) if row[6] is not None else None),
                        "max_density": (float(row[7]) if row[7] is not None else None),
                        "total_readings": row[8],
                        "high_congestion_count": row[9],
                        "severe_congestion_count": row[10],
                        "high_congestion_percentage": (
                            float(row[11]) if row[11] is not None else None
                        ),
                        "severe_congestion_percentage": (
                            float(row[12]) if row[12] is not None else None
                        ),
                    }
                )

            return {"interval": "day", "count": len(data), "data": data}

    finally:
        conn.close()
