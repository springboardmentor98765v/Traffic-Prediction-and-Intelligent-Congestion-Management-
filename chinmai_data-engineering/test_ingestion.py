import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from traffic_ingestion import DATA_FILE, validate_ingestion_row


VALID_RECORD = {
    "road_id": "R001",
    "road_name": "NH16",
    "sensor_id": "S001",
    "timestamp": "2026-08-26 22:00:00",
    "vehicle_count": "28",
    "avg_speed_kmph": "43.3",
    "road_capacity": "100",
    "traffic_density_vehicles_per_km": "5.6",
    "congestion_level": "Low",
    "latitude": "17.738000",
    "longitude": "83.221000",
}


def test_valid_ingestion_record():
    assert validate_ingestion_row(VALID_RECORD) is True


def test_missing_required_field():
    record = VALID_RECORD.copy()
    del record["road_id"]

    with pytest.raises(ValueError, match="Missing required fields"):
        validate_ingestion_row(record)


def test_negative_vehicle_count():
    record = VALID_RECORD.copy()
    record["vehicle_count"] = "-1"

    with pytest.raises(ValueError, match="vehicle_count"):
        validate_ingestion_row(record)


def test_negative_speed():
    record = VALID_RECORD.copy()
    record["avg_speed_kmph"] = "-1"

    with pytest.raises(ValueError, match="avg_speed"):
        validate_ingestion_row(record)


def test_invalid_capacity():
    record = VALID_RECORD.copy()
    record["road_capacity"] = "0"

    with pytest.raises(ValueError, match="road_capacity"):
        validate_ingestion_row(record)


def test_invalid_timestamp():
    record = VALID_RECORD.copy()
    record["timestamp"] = "not-a-date"

    with pytest.raises(ValueError, match="timestamp"):
        validate_ingestion_row(record)


def test_historical_csv_exists_and_has_required_columns():
    assert DATA_FILE.exists()

    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {
            "road_id",
            "sensor_id",
            "timestamp",
            "vehicle_count",
            "avg_speed_kmph",
            "road_capacity",
            "traffic_density_vehicles_per_km",
            "latitude",
            "longitude",
        }
        assert required.issubset(set(reader.fieldnames or []))


def test_first_historical_rows_are_valid():
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append(row)
            if len(rows) == 10:
                break

    assert len(rows) == 10

    for row in rows:
        assert validate_ingestion_row(row) is True
