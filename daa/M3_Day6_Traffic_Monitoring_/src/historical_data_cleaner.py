"""Clean and validate the M2 historical traffic dataset for ML/API use."""

import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data" / "historical_traffic_4weeks.csv"
OUTPUT_FILE = BASE_DIR / "data" / "historical_traffic_4weeks_cleaned.csv"
REPORT_FILE = BASE_DIR / "docs" / "M2_DAY3_DATA_QUALITY_REPORT.md"

REQUIRED_COLUMNS = [
    "road_id",
    "road_name",
    "sensor_id",
    "timestamp",
    "vehicle_count",
    "avg_speed_kmph",
    "road_capacity",
    "congestion_level",
    "latitude",
    "longitude",
    "road_length_km",
    "traffic_density_vehicles_per_km",
    "source",
]


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def clean_rows(rows):
    valid = []
    invalid = []
    seen = set()
    duplicate_count = 0

    for row_number, row in enumerate(rows, start=2):
        try:
            key = (row["road_id"], row["sensor_id"], row["timestamp"])
            if key in seen:
                duplicate_count += 1
                continue

            parse_timestamp(row["timestamp"])  # validates the format
            vehicle_count = int(row["vehicle_count"])
            speed = float(row["avg_speed_kmph"])
            capacity = int(row["road_capacity"])
            density = float(row["traffic_density_vehicles_per_km"])

            if not row["road_id"] or not row["sensor_id"]:
                raise ValueError("missing road_id or sensor_id")
            if vehicle_count < 0 or speed < 0 or capacity <= 0 or density < 0:
                raise ValueError("negative metric or non-positive capacity")
            if row["congestion_level"] not in {"Low", "Medium", "High", "Severe"}:
                raise ValueError("invalid congestion_level")

            seen.add(key)
            valid.append(row)
        except (KeyError, ValueError, TypeError) as exc:
            invalid.append((row_number, str(exc)))

    valid.sort(key=lambda r: (r["road_id"], parse_timestamp(r["timestamp"]), r["sensor_id"]))
    return valid, duplicate_count, invalid


def find_hourly_gaps(rows):
    by_road = defaultdict(list)
    for row in rows:
        by_road[row["road_id"]].append(parse_timestamp(row["timestamp"]))

    gaps = []
    for road_id, timestamps in by_road.items():
        unique = sorted(set(timestamps))
        for previous, current in zip(unique, unique[1:]):
            delta = current - previous
            if delta > timedelta(hours=1):
                missing = int(delta.total_seconds() // 3600) - 1
                gaps.append((road_id, previous.isoformat(), current.isoformat(), missing))
    return gaps


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    with INPUT_FILE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        missing_columns = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

    cleaned, duplicates_removed, invalid_rows = clean_rows(rows)
    gaps = find_hourly_gaps(cleaned)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(cleaned)

    road_counts = Counter(row["road_id"] for row in cleaned)
    start = min((parse_timestamp(r["timestamp"]) for r in cleaned), default=None)
    end = max((parse_timestamp(r["timestamp"]) for r in cleaned), default=None)

    report = "# M2 Day 3 – Historical Data Quality Report\n\n"
    report += f"- Input records: **{len(rows)}**\n"
    report += f"- Cleaned records delivered: **{len(cleaned)}**\n"
    report += f"- Duplicates removed: **{duplicates_removed}**\n"
    report += f"- Invalid rows removed: **{len(invalid_rows)}**\n"
    report += f"- Hourly gaps detected: **{len(gaps)}**\n"
    report += f"- Roads: **{len(road_counts)}**\n"
    report += f"- Start: **{start.isoformat() if start else 'N/A'}**\n"
    report += f"- End: **{end.isoformat() if end else 'N/A'}**\n\n"
    report += "## Records per road\n\n| Road | Records |\n|---|---:|\n"
    for road_id in sorted(road_counts):
        report += f"| {road_id} | {road_counts[road_id]} |\n"
    report += "\n## Gap details\n\n"
    if gaps:
        report += "| Road | Previous | Next | Missing hours |\n|---|---|---|---:|\n"
        for road_id, previous, current, missing in gaps:
            report += f"| {road_id} | {previous} | {current} | {missing} |\n"
    else:
        report += "No hourly gaps detected.\n"
    if invalid_rows:
        report += "\n## Invalid rows\n\n"
        report += "The following rows were excluded during validation:\n\n"
        for row_number, reason in invalid_rows:
            report += f"- CSV row {row_number}: {reason}\n"
    REPORT_FILE.write_text(report, encoding="utf-8")

    print("=" * 60)
    print("M2 DAY 3 - HISTORICAL DATA CLEANING")
    print("=" * 60)
    print(f"Input records: {len(rows)}")
    print(f"Cleaned records: {len(cleaned)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Invalid rows removed: {len(invalid_rows)}")
    print(f"Hourly gaps detected: {len(gaps)}")
    print(f"Cleaned dataset: {OUTPUT_FILE.relative_to(BASE_DIR)}")
    print(f"Quality report: {REPORT_FILE.relative_to(BASE_DIR)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
