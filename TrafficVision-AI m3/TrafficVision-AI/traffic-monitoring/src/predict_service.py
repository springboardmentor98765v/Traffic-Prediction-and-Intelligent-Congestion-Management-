from datetime import datetime

from database import get_postgres_connection

# Add ai-engine/src to Python path
from pathlib import Path
import sys

AI_ENGINE_SRC = Path(__file__).resolve().parents[2] / "ai-engine" / "src"

if str(AI_ENGINE_SRC) not in sys.path:
    sys.path.insert(0, str(AI_ENGINE_SRC))

from predict import predict_congestion


def get_congestion_prediction(road_id: str):
    """
    Fetch the latest traffic reading for a road
    and generate an ML congestion prediction.
    """

    connection = get_postgres_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                tr.road_id,
                tr.vehicle_count,
                tr.avg_speed_kmph,
                tr.traffic_density_vehicles_per_km,
                tr.reading_timestamp,
                r.road_capacity,
                r.road_length_km
            FROM traffic_readings tr
            JOIN roads r
                ON tr.road_id = r.road_id
            WHERE tr.road_id = %s
            ORDER BY tr.reading_timestamp DESC, tr.reading_id DESC
            LIMIT 1
        """

        cursor.execute(query, (road_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        (
            road_id,
            vehicle_count,
            avg_speed_kmph,
            density,
            reading_timestamp,
            road_capacity,
            road_length_km,
        ) = row

        # Convert PostgreSQL numeric values to Python numbers
        vehicle_count = float(vehicle_count)
        avg_speed_kmph = float(avg_speed_kmph)
        density = float(density)
        road_capacity = float(road_capacity)
        road_length_km = float(road_length_km)

        # Timestamp-based features
        hour = reading_timestamp.hour
        day_of_week = reading_timestamp.weekday()
        is_weekend = int(day_of_week >= 5)

        # Run ML prediction
        predicted_level, confidence = predict_congestion(
            vehicle_count=vehicle_count,
            density=density,
            avg_speed_kmph=avg_speed_kmph,
            road_capacity=road_capacity,
            road_length_km=road_length_km,
            hour=hour,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            road_id=road_id,
        )

        return {
            "road_id": road_id,
            "predicted_level": predicted_level,
            "confidence": round(confidence, 4),
            "generated_by": "model-v1",
        }

    finally:
        connection.close()
def get_peak_hour_prediction(road_id: str):
    """
    Predict congestion levels for predefined peak-hour periods
    using the trained ML model and the latest traffic reading.
    """

    connection = get_postgres_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                tr.road_id,
                tr.vehicle_count,
                tr.avg_speed_kmph,
                tr.traffic_density_vehicles_per_km,
                r.road_capacity,
                r.road_length_km
            FROM traffic_readings tr
            JOIN roads r
                ON tr.road_id = r.road_id
            WHERE tr.road_id = %s
            ORDER BY tr.reading_timestamp DESC, tr.reading_id DESC
            LIMIT 1
        """

        cursor.execute(query, (road_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        (
            road_id,
            vehicle_count,
            avg_speed_kmph,
            density,
            road_capacity,
            road_length_km,
        ) = row

        vehicle_count = float(vehicle_count)
        avg_speed_kmph = float(avg_speed_kmph)
        density = float(density)
        road_capacity = float(road_capacity)
        road_length_km = float(road_length_km)

        # Common peak-hour periods.
        peak_hours = [8, 9, 10, 17, 18, 19, 20]

        predictions = []

        for hour in peak_hours:

            # Weekday baseline for the current model.
            day_of_week = 0
            is_weekend = 0

            predicted_level, confidence = predict_congestion(
                vehicle_count=vehicle_count,
                density=density,
                avg_speed_kmph=avg_speed_kmph,
                road_capacity=road_capacity,
                road_length_km=road_length_km,
                hour=hour,
                day_of_week=day_of_week,
                is_weekend=is_weekend,
                road_id=road_id,
            )

            predictions.append(
                {
                    "hour": hour,
                    "predicted_level": predicted_level,
                    "confidence": round(confidence, 4),
                }
            )

        return {
            "road_id": road_id,
            "peak_hours": predictions,
            "generated_by": "model-v1",
        }

    finally:
        connection.close()
def get_delay_prediction(road_id: str):
    """
    Estimate travel delay for a road using the latest traffic reading.

    Delay is calculated by comparing current travel time
    with a 50 km/h reference free-flow travel time.
    """

    connection = get_postgres_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                tr.road_id,
                tr.avg_speed_kmph,
                tr.reading_timestamp,
                r.road_length_km
            FROM traffic_readings tr
            JOIN roads r
                ON tr.road_id = r.road_id
            WHERE tr.road_id = %s
            ORDER BY tr.reading_timestamp DESC, tr.reading_id DESC
            LIMIT 1
        """

        cursor.execute(query, (road_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        (
            road_id,
            avg_speed_kmph,
            reading_timestamp,
            road_length_km,
        ) = row

        avg_speed_kmph = float(avg_speed_kmph)
        road_length_km = float(road_length_km)

        free_flow_speed_kmph = 50.0

        if avg_speed_kmph <= 0:
            return None

        current_travel_time_minutes = (
            road_length_km / avg_speed_kmph
        ) * 60

        free_flow_travel_time_minutes = (
            road_length_km / free_flow_speed_kmph
        ) * 60

        delay_minutes = max(
            0,
            current_travel_time_minutes
            - free_flow_travel_time_minutes
        )

        return {
            "road_id": road_id,
            "avg_speed_kmph": round(avg_speed_kmph, 2),
            "road_length_km": round(road_length_km, 2),
            "estimated_travel_time_minutes": round(
                current_travel_time_minutes, 2
            ),
            "free_flow_travel_time_minutes": round(
                free_flow_travel_time_minutes, 2
            ),
            "estimated_delay_minutes": round(
                delay_minutes, 2
            ),
            "reference_free_flow_speed_kmph": free_flow_speed_kmph,
            "reading_timestamp": reading_timestamp.isoformat(),
            "generated_by": "baseline-delay-v1",
        }

    finally:
        connection.close()