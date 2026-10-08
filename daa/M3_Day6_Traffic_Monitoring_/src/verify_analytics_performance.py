from database import get_postgres_connection

REPORT_QUERY = """
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    road_id,
    sensor_id,
    reading_timestamp,
    vehicle_count,
    avg_speed_kmph,
    road_capacity,
    traffic_density_vehicles_per_km,
    congestion_level,
    latitude,
    longitude,
    source
FROM traffic_history
WHERE road_id = %s
  AND reading_timestamp >= %s::date
  AND reading_timestamp < (%s::date + INTERVAL '1 day')
ORDER BY reading_timestamp ASC, history_id ASC
LIMIT 10000;
"""

HEATMAP_QUERY = """
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    road_id,
    EXTRACT(
        HOUR FROM (reading_timestamp AT TIME ZONE 'Asia/Kolkata')
    )::integer AS hour_of_day,
    AVG(vehicle_count),
    AVG(avg_speed_kmph),
    AVG(traffic_density_vehicles_per_km),
    COUNT(*)
FROM traffic_history
WHERE reading_timestamp >= %s::date
  AND reading_timestamp < (%s::date + INTERVAL '1 day')
GROUP BY road_id, hour_of_day
ORDER BY road_id, hour_of_day;
"""


def print_plan(cursor, title, query, params):
    cursor.execute(query, params)
    print(f"\n=== {title} ===")
    for row in cursor.fetchall():
        print(row[0])


def main():
    conn = get_postgres_connection()
    try:
        cursor = conn.cursor()
        print_plan(
            cursor,
            "Historical report query",
            REPORT_QUERY,
            ("R001", "2026-07-27", "2026-08-23"),
        )
        print_plan(
            cursor,
            "Heatmap aggregation query",
            HEATMAP_QUERY,
            ("2026-07-27", "2026-08-23"),
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
