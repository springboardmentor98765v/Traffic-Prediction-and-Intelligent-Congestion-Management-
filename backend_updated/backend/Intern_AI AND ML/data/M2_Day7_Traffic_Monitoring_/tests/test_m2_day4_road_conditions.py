from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


def test_road_condition_csv_exists_and_has_required_columns():
    path = PROJECT_ROOT / "data" / "road_conditions.csv"
    assert path.exists()

    df = pd.read_csv(path)
    required = {
        "road_id",
        "condition_timestamp",
        "road_condition",
        "road_status",
        "incident_type",
        "description",
        "source",
    }
    assert required.issubset(df.columns)
    assert len(df) == 9


def test_road_condition_values_are_valid():
    path = PROJECT_ROOT / "data" / "road_conditions.csv"
    df = pd.read_csv(path)

    assert df["road_id"].notna().all()
    assert df["condition_timestamp"].notna().all()
    assert set(df["road_status"]).issubset({"Active", "Resolved", "Planned"})


def test_road_condition_endpoint_is_registered():
    from main import app

    routes = {route.path for route in app.routes}
    assert "/api/v1/traffic/road-condition/{road_id}" in routes
