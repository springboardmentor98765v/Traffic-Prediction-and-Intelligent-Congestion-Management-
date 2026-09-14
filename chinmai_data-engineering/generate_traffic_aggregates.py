"""
M2 Day 5 - Generate Hourly and Daily Traffic Metrics.

Reads traffic_history and creates/refreshes:
    hourly_traffic_metrics
    daily_traffic_metrics
"""

from database import get_postgres_connection


def generate_hourly_metrics():
    query = """
        INSERT INTO hourly_traffic_metrics (
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
        )
        SELECT
            road_id,
            date_trunc('hour', reading_timestamp) AS metric_timestamp,

            ROUND(AVG(vehicle_count)::numeric, 2),
            MAX(vehicle_count),

            ROUND(AVG(avg_speed_kmph)::numeric, 2),
            ROUND(MIN(avg_speed_kmph)::numeric, 2),

            ROUND(
                AVG(traffic_density_vehicles_per_km)::numeric,
                2
            ),

            ROUND(
                MAX(traffic_density_vehicles_per_km)::numeric,
                2
            ),

            COUNT(*),

            COUNT(*) FILTER (
                WHERE congestion_level = 'High'
            ),

            COUNT(*) FILTER (
                WHERE congestion_level = 'Severe'
            ),

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE congestion_level = 'High'
                    )::numeric
                    / NULLIF(COUNT(*), 0)
                ) * 100,
                2
            ),

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE congestion_level = 'Severe'
                    )::numeric
                    / NULLIF(COUNT(*), 0)
                ) * 100,
                2
            )

        FROM traffic_history

        GROUP BY
            road_id,
            date_trunc('hour', reading_timestamp)

        ON CONFLICT (road_id, metric_timestamp)
        DO UPDATE SET
            avg_vehicle_count =
                EXCLUDED.avg_vehicle_count,

            max_vehicle_count =
                EXCLUDED.max_vehicle_count,

            avg_speed_kmph =
                EXCLUDED.avg_speed_kmph,

            min_speed_kmph =
                EXCLUDED.min_speed_kmph,

            avg_density =
                EXCLUDED.avg_density,

            max_density =
                EXCLUDED.max_density,

            total_readings =
                EXCLUDED.total_readings,

            high_congestion_count =
                EXCLUDED.high_congestion_count,

            severe_congestion_count =
                EXCLUDED.severe_congestion_count,

            high_congestion_percentage =
                EXCLUDED.high_congestion_percentage,

            severe_congestion_percentage =
                EXCLUDED.severe_congestion_percentage;
    """

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            count = cursor.rowcount

        conn.commit()

        return count

    finally:
        conn.close()


def generate_daily_metrics():
    query = """
        INSERT INTO daily_traffic_metrics (
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
        )
        SELECT
            road_id,
            DATE(reading_timestamp) AS metric_date,

            ROUND(AVG(vehicle_count)::numeric, 2),
            MAX(vehicle_count),

            ROUND(AVG(avg_speed_kmph)::numeric, 2),
            ROUND(MIN(avg_speed_kmph)::numeric, 2),

            ROUND(
                AVG(traffic_density_vehicles_per_km)::numeric,
                2
            ),

            ROUND(
                MAX(traffic_density_vehicles_per_km)::numeric,
                2
            ),

            COUNT(*),

            COUNT(*) FILTER (
                WHERE congestion_level = 'High'
            ),

            COUNT(*) FILTER (
                WHERE congestion_level = 'Severe'
            ),

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE congestion_level = 'High'
                    )::numeric
                    / NULLIF(COUNT(*), 0)
                ) * 100,
                2
            ),

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE congestion_level = 'Severe'
                    )::numeric
                    / NULLIF(COUNT(*), 0)
                ) * 100,
                2
            )

        FROM traffic_history

        GROUP BY
            road_id,
            DATE(reading_timestamp)

        ON CONFLICT (road_id, metric_date)
        DO UPDATE SET
            avg_vehicle_count =
                EXCLUDED.avg_vehicle_count,

            max_vehicle_count =
                EXCLUDED.max_vehicle_count,

            avg_speed_kmph =
                EXCLUDED.avg_speed_kmph,

            min_speed_kmph =
                EXCLUDED.min_speed_kmph,

            avg_density =
                EXCLUDED.avg_density,

            max_density =
                EXCLUDED.max_density,

            total_readings =
                EXCLUDED.total_readings,

            high_congestion_count =
                EXCLUDED.high_congestion_count,

            severe_congestion_count =
                EXCLUDED.severe_congestion_count,

            high_congestion_percentage =
                EXCLUDED.high_congestion_percentage,

            severe_congestion_percentage =
                EXCLUDED.severe_congestion_percentage;
    """

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            count = cursor.rowcount

        conn.commit()

        return count

    finally:
        conn.close()


def main():
    print("=" * 60)
    print("M2 DAY 5 - TRAFFIC AGGREGATION")
    print("=" * 60)

    hourly = generate_hourly_metrics()

    print(
        f"Hourly aggregation rows processed: {hourly}"
    )

    daily = generate_daily_metrics()

    print(
        f"Daily aggregation rows processed: {daily}"
    )

    print("=" * 60)
    print("Traffic aggregation completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()