import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from historical_data_cleaner import clean_rows, find_hourly_gaps


def row(ts, road="R001", sensor="S001"):
    return {
        "road_id": road,
        "sensor_id": sensor,
        "timestamp": ts,
        "vehicle_count": "10",
        "avg_speed_kmph": "40",
        "road_capacity": "100",
        "traffic_density_vehicles_per_km": "5",
        "congestion_level": "Low",
    }


def test_duplicate_is_removed():
    rows = [row("2026-07-27T00:00:00+05:30"), row("2026-07-27T00:00:00+05:30")]
    cleaned, duplicates, invalid = clean_rows(rows)
    assert len(cleaned) == 1
    assert duplicates == 1
    assert invalid == []


def test_hourly_gap_is_detected():
    rows = [row("2026-07-27T00:00:00+05:30"), row("2026-07-27T02:00:00+05:30")]
    assert find_hourly_gaps(rows)[0][3] == 1
