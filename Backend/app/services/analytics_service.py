import io
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from app.services import traffic_service
from app.services.traffic_service import ROAD_NAMES

CONGESTION_NUMERIC = {
    "low": 0.25,
    "medium": 0.60,
    "high": 0.90
}


def _congestion_to_numeric(level: str) -> float:
    return CONGESTION_NUMERIC.get(str(level).strip().lower(), 0.5)


def get_traffic_trends(road_id: str, range_type: str = "day") -> Dict[str, Any]:
    """
    FR-05: System provides a traffic-trend-analysis endpoint (daily/weekly patterns per road).
    Returns hourly or daily rolled-up congestion intensity and traffic KPIs.
    """
    normalized_id = road_id.strip().upper()
    range_clean = range_type.strip().lower()
    if range_clean not in ["day", "week"]:
        range_clean = "day"

    records = traffic_service.load_traffic_records()
    road_records = [r for r in records if r.get("road_id", "").upper() == normalized_id]

    if not road_records:
        # Fallback empty profile
        return {
            "road_id": normalized_id,
            "range": range_clean,
            "points": [],
            "summary": {"message": f"No historical records found for road {normalized_id}"}
        }

    df = pd.DataFrame(road_records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["density"] = pd.to_numeric(df["density"], errors="coerce").fillna(25.0)
    df["avg_speed"] = pd.to_numeric(df["avg_speed"], errors="coerce").fillna(40.0)
    df["numeric_congestion"] = df["congestion"].apply(_congestion_to_numeric)

    points = []
    if range_clean == "day":
        # Group by hour (0 to 23)
        df["hour"] = df["timestamp"].dt.hour
        grouped = df.groupby("hour").agg({
            "numeric_congestion": "mean",
            "avg_speed": "mean",
            "density": "mean"
        }).reset_index()

        for h in range(24):
            match = grouped[grouped["hour"] == h]
            if not match.empty:
                row = match.iloc[0]
                score = round(float(row["numeric_congestion"]), 3)
                speed = round(float(row["avg_speed"]), 1)
                dens = round(float(row["density"]), 1)
            else:
                score = 0.35
                speed = 45.0
                dens = 25.0

            label = "Low" if score < 0.4 else ("Medium" if score < 0.75 else "High")
            points.append({
                "period": f"{h:02d}:00",
                "avg_congestion": score,
                "avg_speed": speed,
                "avg_density": dens,
                "congestion_label": label
            })

    else:
        # Group by day of week (Monday to Sunday)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df["day_name"] = df["timestamp"].dt.day_name()
        grouped = df.groupby("day_name").agg({
            "numeric_congestion": "mean",
            "avg_speed": "mean",
            "density": "mean"
        }).reset_index()

        for day in days:
            match = grouped[grouped["day_name"] == day]
            if not match.empty:
                row = match.iloc[0]
                score = round(float(row["numeric_congestion"]), 3)
                speed = round(float(row["avg_speed"]), 1)
                dens = round(float(row["density"]), 1)
            else:
                score = 0.40
                speed = 42.0
                dens = 30.0

            label = "Low" if score < 0.4 else ("Medium" if score < 0.75 else "High")
            points.append({
                "period": day,
                "avg_congestion": score,
                "avg_speed": speed,
                "avg_density": dens,
                "congestion_label": label
            })

    avg_all = round(float(df["numeric_congestion"].mean()), 2)
    return {
        "road_id": normalized_id,
        "range": range_clean,
        "points": points,
        "summary": {
            "overall_avg_congestion": avg_all,
            "total_samples": len(df),
            "road_name": ROAD_NAMES.get(normalized_id, normalized_id)
        }
    }


def get_congestion_heatmap(range_type: str = "day") -> Dict[str, Any]:
    """
    FR-06: System generates congestion heatmap data across roads and time buckets.
    Returns a 2D matrix structure ready for frontend grid/heatmap rendering.
    """
    range_clean = range_type.strip().lower()
    if range_clean not in ["day", "week"]:
        range_clean = "day"

    records = traffic_service.load_traffic_records()
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["road_id"] = df["road_id"].str.upper()
    df["numeric_congestion"] = df["congestion"].apply(_congestion_to_numeric)

    roads = list(ROAD_NAMES.keys())
    road_labels = [ROAD_NAMES[r] for r in roads]

    if range_clean == "day":
        # 6 4-hour buckets
        time_buckets = [
            "00:00-04:00",
            "04:00-08:00",
            "08:00-12:00",
            "12:00-16:00",
            "16:00-20:00",
            "20:00-24:00"
        ]

        def get_bucket(hour: int) -> str:
            if 0 <= hour < 4:
                return "00:00-04:00"
            elif 4 <= hour < 8:
                return "04:00-08:00"
            elif 8 <= hour < 12:
                return "08:00-12:00"
            elif 12 <= hour < 16:
                return "12:00-16:00"
            elif 16 <= hour < 20:
                return "16:00-20:00"
            else:
                return "20:00-24:00"

        df["bucket"] = df["timestamp"].dt.hour.apply(get_bucket)
    else:
        time_buckets = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df["bucket"] = df["timestamp"].dt.day_name()

    pivot = df.pivot_table(
        index="road_id",
        columns="bucket",
        values="numeric_congestion",
        aggfunc="mean"
    ).fillna(0.35)

    matrix = []
    for r in roads:
        row_vals = []
        for b in time_buckets:
            val = float(pivot.loc[r, b]) if (r in pivot.index and b in pivot.columns) else 0.35
            row_vals.append(round(val, 2))
        matrix.append(row_vals)

    return {
        "range": range_clean,
        "roads": roads,
        "road_names": road_labels,
        "time_buckets": time_buckets,
        "values": matrix
    }


def generate_historical_report(range_type: str = "week", format_type: str = "json") -> Any:
    """
    FR-07: System generates downloadable historical traffic reports (CSV or JSON).
    """
    records = traffic_service.load_traffic_records()
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["road_id"] = df["road_id"].str.upper()
    df["density"] = pd.to_numeric(df["density"], errors="coerce").fillna(25.0)
    df["avg_speed"] = pd.to_numeric(df["avg_speed"], errors="coerce").fillna(40.0)

    total_records = len(df)
    total_roads = df["road_id"].nunique()
    avg_speed = round(float(df["avg_speed"].mean()), 2)
    avg_density = round(float(df["density"].mean()), 2)
    high_incidents = int((df["congestion"].str.lower() == "high").sum())

    # Find road with highest congestion count
    road_highs = df[df["congestion"].str.lower() == "high"]["road_id"].value_counts()
    peak_road = road_highs.index[0] if not road_highs.empty else "R001"

    if format_type.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["reading_id", "road_id", "road_name", "timestamp", "vehicle_count", "avg_speed", "density", "congestion"])
        for idx, row in df.iterrows():
            rid = str(row.get("road_id", ""))
            writer.writerow([
                row.get("reading_id", idx + 1),
                rid,
                ROAD_NAMES.get(rid, rid),
                row.get("timestamp"),
                row.get("vehicle_count"),
                row.get("avg_speed"),
                row.get("density"),
                row.get("congestion")
            ])
        return output.getvalue()

    sample_records = []
    for _, row in df.tail(50).iterrows():
        rid = str(row.get("road_id", ""))
        sample_records.append({
            "road_id": rid,
            "road_name": ROAD_NAMES.get(rid, rid),
            "timestamp": str(row.get("timestamp")),
            "density": float(row.get("density", 0)),
            "avg_speed": float(row.get("avg_speed", 0)),
            "congestion": row.get("congestion")
        })

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "range": range_type,
        "total_records": total_records,
        "total_roads": total_roads,
        "average_city_speed": avg_speed,
        "average_city_density": avg_density,
        "high_congestion_incidents": high_incidents,
        "peak_congestion_road": f"{ROAD_NAMES.get(peak_road, peak_road)} ({peak_road})",
        "records": sample_records
    }
