import csv
import io

from database import get_postgres_connection

REPORT_COLUMNS = [
    "road_id",
    "sensor_id",
    "reading_timestamp",
    "vehicle_count",
    "avg_speed_kmph",
    "road_capacity",
    "traffic_density_vehicles_per_km",
    "congestion_level",
    "latitude",
    "longitude",
    "source",
]


def generate_historical_report(
    road_id=None,
    start_date=None,
    end_date=None,
    limit=10000,
):
    """
    Generate historical traffic data as CSV text.

    Date filtering uses Asia/Kolkata so the report matches
    the Trends and Heatmap analytics services.
    """

    if limit < 1 or limit > 50000:
        raise ValueError("limit must be between 1 and 50000")

    conn = get_postgres_connection()

    try:
        cursor = conn.cursor()

        query = """
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
            WHERE 1 = 1
        """

        params = []

        # -------------------------------------------------
        # ROAD FILTER
        # -------------------------------------------------

        if road_id:
            query += """
                AND road_id = %s
            """

            params.append(road_id)

        # -------------------------------------------------
        # START DATE
        # Asia/Kolkata date semantics
        # -------------------------------------------------

        if start_date:
            query += """
                AND (
                    reading_timestamp
                    AT TIME ZONE 'Asia/Kolkata'
                )::date >= %s::date
            """

            params.append(start_date)

        # -------------------------------------------------
        # END DATE
        # Asia/Kolkata date semantics
        # -------------------------------------------------

        if end_date:
            query += """
                AND (
                    reading_timestamp
                    AT TIME ZONE 'Asia/Kolkata'
                )::date <= %s::date
            """

            params.append(end_date)

        # -------------------------------------------------
        # ORDER + LIMIT
        # -------------------------------------------------

        query += """
            ORDER BY
                reading_timestamp ASC,
                history_id ASC
            LIMIT %s
        """

        params.append(limit)

        cursor.execute(query, tuple(params))

        rows = cursor.fetchall()

        # -------------------------------------------------
        # CSV GENERATION
        # -------------------------------------------------

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow(REPORT_COLUMNS)

        for row in rows:
            writer.writerow(
                [(value.isoformat() if hasattr(value, "isoformat") else value) for value in row]
            )

        return output.getvalue(), len(rows)

    finally:
        conn.close()
