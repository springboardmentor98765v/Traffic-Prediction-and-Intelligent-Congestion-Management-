from database import get_postgres_connection


CONGESTION_SCORE = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Severe": 4,
}


def get_traffic_heatmap(
    start_date=None,
    end_date=None,
    time_bucket="hour"
):
    """
    Return frontend-ready road x time-bucket heatmap data.

    Uses M2 traffic_history time-series data.
    """

    if time_bucket not in {"hour", "day"}:
        raise ValueError("time_bucket must be 'hour' or 'day'")

    conn = get_postgres_connection()

    try:
        # FIX: Do not use "with conn.cursor()"
        # because the test FakeCursor does not implement
        # the context manager protocol.
        cursor = conn.cursor()

        if time_bucket == "hour":
            bucket_expression = """
                EXTRACT(
                    HOUR FROM (
                        reading_timestamp
                        AT TIME ZONE 'Asia/Kolkata'
                    )
                )::integer
            """
        else:
            bucket_expression = """
                (
                    reading_timestamp
                    AT TIME ZONE 'Asia/Kolkata'
                )::date
            """

        query = f"""
            SELECT
                road_id,
                {bucket_expression} AS time_bucket,
                ROUND(AVG(vehicle_count), 2) AS avg_vehicle_count,
                ROUND(AVG(avg_speed_kmph), 2) AS avg_speed_kmph,
                ROUND(
                    AVG(traffic_density_vehicles_per_km),
                    2
                ) AS avg_density,
                ROUND(
                    MAX(traffic_density_vehicles_per_km),
                    2
                ) AS max_density,
                COUNT(*) AS total_readings,
                COUNT(*) FILTER (
                    WHERE congestion_level = 'Low'
                ) AS low_count,
                COUNT(*) FILTER (
                    WHERE congestion_level = 'Medium'
                ) AS medium_count,
                COUNT(*) FILTER (
                    WHERE congestion_level = 'High'
                ) AS high_count,
                COUNT(*) FILTER (
                    WHERE congestion_level = 'Severe'
                ) AS severe_count
            FROM traffic_history
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += """
                AND (
                    reading_timestamp
                    AT TIME ZONE 'Asia/Kolkata'
                )::date >= %s
            """
            params.append(start_date)

        if end_date:
            query += """
                AND (
                    reading_timestamp
                    AT TIME ZONE 'Asia/Kolkata'
                )::date <= %s
            """
            params.append(end_date)

        query += f"""
            GROUP BY
                road_id,
                {bucket_expression}
            ORDER BY
                road_id,
                time_bucket
        """

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        grid = []
        roads = set()
        time_buckets = set()

        for row in rows:
            (
                road_id,
                time_bucket_value,
                avg_vehicle_count,
                avg_speed,
                avg_density,
                max_density,
                total_readings,
                low_count,
                medium_count,
                high_count,
                severe_count,
            ) = row

            roads.add(road_id)
            time_buckets.add(str(time_bucket_value))

            # Calculate weighted congestion score.
            if total_readings:
                congestion_score = round(
                    (
                        low_count * CONGESTION_SCORE["Low"]
                        + medium_count * CONGESTION_SCORE["Medium"]
                        + high_count * CONGESTION_SCORE["High"]
                        + severe_count * CONGESTION_SCORE["Severe"]
                    )
                    / total_readings,
                    2
                )
            else:
                congestion_score = 0

            level_counts = {
                "Low": low_count,
                "Medium": medium_count,
                "High": high_count,
                "Severe": severe_count,
            }

            dominant_level = max(
                level_counts,
                key=level_counts.get
            )

            grid.append(
                {
                    "road_id": road_id,
                    "time_bucket": (
                        int(time_bucket_value)
                        if time_bucket == "hour"
                        else str(time_bucket_value)
                    ),
                    "avg_vehicle_count": float(avg_vehicle_count),
                    "avg_speed_kmph": (
                        float(avg_speed)
                        if avg_speed is not None
                        else None
                    ),
                    "avg_density": float(avg_density),
                    "max_density": float(max_density),
                    "congestion_score": congestion_score,
                    "congestion_level": dominant_level,
                    "total_readings": total_readings,
                    "low_count": low_count,
                    "medium_count": medium_count,
                    "high_count": high_count,
                    "severe_count": severe_count,
                }
            )

        return {
            "source": "M2 traffic_history",
            "time_bucket": time_bucket,
            "roads": sorted(roads),
            "time_buckets": sorted(
                time_buckets,
                key=lambda value: (
                    int(value)
                    if time_bucket == "hour"
                    else value
                )
            ),
            "grid": grid,
        }

    finally:
        conn.close()