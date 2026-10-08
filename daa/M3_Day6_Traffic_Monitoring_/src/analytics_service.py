from database import get_postgres_connection


def get_traffic_trends(road_id, start_date=None, end_date=None):
    """
    Return daily traffic trends and weekly
    recurring traffic patterns for a road.

    Uses M2 traffic_history time-series data.
    """

    if not road_id:
        raise ValueError("road_id is required")

    conn = get_postgres_connection()

    try:
        with conn.cursor() as cursor:

            # =====================================================
            # DAILY TREND
            # =====================================================

            daily_query = """
                SELECT
                    road_id,
                    (
                        reading_timestamp
                        AT TIME ZONE 'Asia/Kolkata'
                    )::date AS trend_date,

                    ROUND(
                        AVG(vehicle_count),
                        2
                    ) AS avg_vehicle_count,

                    MAX(vehicle_count)
                        AS max_vehicle_count,

                    ROUND(
                        AVG(avg_speed_kmph),
                        2
                    ) AS avg_speed_kmph,

                    ROUND(
                        AVG(
                            traffic_density_vehicles_per_km
                        ),
                        2
                    ) AS avg_density,

                    ROUND(
                        MAX(
                            traffic_density_vehicles_per_km
                        ),
                        2
                    ) AS max_density,

                    COUNT(*) AS total_readings,

                    COUNT(*) FILTER (
                        WHERE congestion_level = 'High'
                    ) AS high_congestion_count,

                    COUNT(*) FILTER (
                        WHERE congestion_level = 'Severe'
                    ) AS severe_congestion_count

                FROM traffic_history

                WHERE road_id = %s
            """

            daily_params = [road_id]

            if start_date:
                daily_query += """
                    AND (
                        reading_timestamp
                        AT TIME ZONE 'Asia/Kolkata'
                    )::date >= %s
                """
                daily_params.append(start_date)

            if end_date:
                daily_query += """
                    AND (
                        reading_timestamp
                        AT TIME ZONE 'Asia/Kolkata'
                    )::date <= %s
                """
                daily_params.append(end_date)

            daily_query += """
                GROUP BY
                    road_id,
                    (
                        reading_timestamp
                        AT TIME ZONE 'Asia/Kolkata'
                    )::date

                ORDER BY trend_date ASC
            """

            cursor.execute(daily_query, tuple(daily_params))

            daily_rows = cursor.fetchall()

            daily_trends = []

            for row in daily_rows:

                total_readings = row[7]

                high_percentage = round((row[8] / total_readings) * 100, 2) if total_readings else 0

                severe_percentage = (
                    round((row[9] / total_readings) * 100, 2) if total_readings else 0
                )

                daily_trends.append(
                    {
                        "road_id": row[0],
                        "time_period": str(row[1]),
                        "avg_vehicle_count": float(row[2]),
                        "max_vehicle_count": row[3],
                        "avg_speed_kmph": (float(row[4]) if row[4] is not None else None),
                        "avg_density": float(row[5]),
                        "max_density": float(row[6]),
                        "total_readings": total_readings,
                        "high_congestion_count": row[8],
                        "severe_congestion_count": row[9],
                        "high_congestion_percentage": (high_percentage),
                        "severe_congestion_percentage": (severe_percentage),
                    }
                )

            # =====================================================
            # WEEKLY RECURRING PATTERN
            # =====================================================

            weekly_query = """
                SELECT
                    road_id,

                    EXTRACT(
                        ISODOW FROM (
                            reading_timestamp
                            AT TIME ZONE 'Asia/Kolkata'
                        )
                    )::integer AS day_of_week_number,

                    TO_CHAR(
                        (
                            reading_timestamp
                            AT TIME ZONE 'Asia/Kolkata'
                        ),
                        'Day'
                    ) AS day_of_week,

                    EXTRACT(
                        HOUR FROM (
                            reading_timestamp
                            AT TIME ZONE 'Asia/Kolkata'
                        )
                    )::integer AS hour_of_day,

                    ROUND(
                        AVG(vehicle_count),
                        2
                    ) AS avg_vehicle_count,

                    MAX(vehicle_count)
                        AS max_vehicle_count,

                    ROUND(
                        AVG(avg_speed_kmph),
                        2
                    ) AS avg_speed_kmph,

                    ROUND(
                        AVG(
                            traffic_density_vehicles_per_km
                        ),
                        2
                    ) AS avg_density,

                    ROUND(
                        MAX(
                            traffic_density_vehicles_per_km
                        ),
                        2
                    ) AS max_density,

                    COUNT(*) AS total_readings,

                    COUNT(*) FILTER (
                        WHERE congestion_level = 'High'
                    ) AS high_congestion_count,

                    COUNT(*) FILTER (
                        WHERE congestion_level = 'Severe'
                    ) AS severe_congestion_count

                FROM traffic_history

                WHERE road_id = %s
            """

            weekly_params = [road_id]

            if start_date:
                weekly_query += """
                    AND (
                        reading_timestamp
                        AT TIME ZONE 'Asia/Kolkata'
                    )::date >= %s
                """
                weekly_params.append(start_date)

            if end_date:
                weekly_query += """
                    AND (
                        reading_timestamp
                        AT TIME ZONE 'Asia/Kolkata'
                    )::date <= %s
                """
                weekly_params.append(end_date)

            weekly_query += """
                GROUP BY
                    road_id,
                    day_of_week_number,
                    day_of_week,
                    hour_of_day

                ORDER BY
                    day_of_week_number,
                    hour_of_day
            """

            cursor.execute(weekly_query, tuple(weekly_params))

            weekly_rows = cursor.fetchall()

            weekly_pattern = []

            for row in weekly_rows:

                total_readings = row[9]

                high_percentage = (
                    round((row[10] / total_readings) * 100, 2) if total_readings else 0
                )

                severe_percentage = (
                    round((row[11] / total_readings) * 100, 2) if total_readings else 0
                )

                weekly_pattern.append(
                    {
                        "road_id": row[0],
                        "day_of_week": row[2].strip(),
                        "day_of_week_number": row[1],
                        "hour_of_day": row[3],
                        "avg_vehicle_count": float(row[4]),
                        "max_vehicle_count": row[5],
                        "avg_speed_kmph": (float(row[6]) if row[6] is not None else None),
                        "avg_density": float(row[7]),
                        "max_density": float(row[8]),
                        "total_readings": total_readings,
                        "high_congestion_count": row[10],
                        "severe_congestion_count": row[11],
                        "high_congestion_percentage": (high_percentage),
                        "severe_congestion_percentage": (severe_percentage),
                    }
                )

            return {
                "road_id": road_id,
                "source": "M2 traffic_history",
                "daily_trends": daily_trends,
                "weekly_pattern": weekly_pattern,
            }

    finally:
        conn.close()
