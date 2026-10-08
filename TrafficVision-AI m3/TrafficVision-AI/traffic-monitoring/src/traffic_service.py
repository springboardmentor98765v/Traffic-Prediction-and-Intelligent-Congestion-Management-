import os

from database import get_postgres_connection

from redis_cache import (
    get_redis_client,
    get_cached_live_traffic,
    cache_live_traffic,
)


# Cache live traffic for 30 seconds by default
LIVE_CACHE_TTL = int(
    os.getenv("REDIS_TTL_SECONDS", "30")
)


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

            cached_data = get_cached_live_traffic(
                redis_client
            )

            if cached_data is not None:

                print(
                    "Redis HIT: traffic:live"
                )

                return cached_data

            print(
                "Redis MISS: traffic:live"
            )

        except Exception as redis_error:

            print(
                f"Redis read error: {redis_error}"
            )

            print(
                "Continuing with PostgreSQL..."
            )

        # -------------------------------------------------
        # STEP 2: Get latest traffic from PostgreSQL
        # -------------------------------------------------

        print(
            "Fetching live traffic from PostgreSQL"
        )

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
                            "updated_at": row[4].isoformat()
                        }
                    )

        finally:

            conn.close()

        # -------------------------------------------------
        # STEP 3: Store result in Redis
        # -------------------------------------------------

        try:

            cache_live_traffic(
                redis_client,
                result,
                LIVE_CACHE_TTL
            )

            print(
                "Cached traffic:live in Redis"
            )

            print(
                f"Cache TTL: {LIVE_CACHE_TTL} seconds"
            )

        except Exception as redis_error:

            print(
                f"Redis write error: {redis_error}"
            )

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

            cursor.execute(
                road_query,
                (road_id,)
            )

            road = cursor.fetchone()

            if road is None:

                return None

            # ---------------------------------------------
            # Get history
            # ---------------------------------------------

            cursor.execute(
                history_query,
                (road_id,)
            )

            rows = cursor.fetchall()

            if not rows:

                return {
                    "road_id": road[0],
                    "name": road[1],
                    "congestion_level": "Unknown",
                    "history": []
                }

            # Latest reading
            latest = rows[0]

            history = []

            for row in rows:

                history.append(
                    {
                        "vehicle_count": row[0],

                        "density": float(
                            row[1]
                        ),

                        "congestion_level": row[2],

                        "avg_speed_kmph": (
                            float(row[4])
                            if row[4] is not None
                            else None
                        ),

                        "updated_at": (
                            row[3].isoformat()
                        )
                    }
                )

            return {
                "road_id": road[0],
                "name": road[1],
                "congestion_level": latest[2],
                "history": history
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

                "average_density": round(
                    float(row[1]),
                    2
                ),

                "maximum_density": round(
                    float(row[2]),
                    2
                ),

                "minimum_density": round(
                    float(row[3]),
                    2
                ),

                "high_congestion_roads": row[4],

                "severe_congestion_roads": row[5],

                "total_vehicle_count": row[6]
            }

    finally:

        conn.close()