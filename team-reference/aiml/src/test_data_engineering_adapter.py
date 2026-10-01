import pandas as pd

from src.data_engineering_adapter import TrafficDataAdapter


def test_external_schema_maps_to_model_schema():
    frame = TrafficDataAdapter._canonicalize([
        {
            "road_id": 1,
            "vehicle_count": 90,
            "avg_speed_kmph": 44,
            "density": 12.5,
            "congestion_level": "MODERATE",
            "recorded_at": "2026-09-21T08:15:00",
        }
    ])

    assert frame.to_dict(orient="records") == [{
        "road_id": "R001",
        "vehicle_count": 90,
        "average_speed": 44,
        "density": 12.5,
        "congestion_level": "MEDIUM",
        "timestamp": pd.Timestamp("2026-09-21T08:15:00"),
    }]


def test_local_source_remains_available_without_external_url(tmp_path):
    csv_path = tmp_path / "traffic.csv"
    csv_path.write_text(
        "road_id,timestamp,vehicle_count,average_speed,congestion_level\n"
        "R001,2026-09-21T08:00:00,80,45,LOW\n",
        encoding="utf-8",
    )

    adapter = TrafficDataAdapter(csv_path)
    frame = adapter.load_history()

    assert adapter.source_name() == "local-processed-csv"
    assert frame.iloc[0]["road_id"] == "R001"
    assert frame.iloc[0]["average_speed"] == 45


def test_external_road_ids_are_normalized_to_source_model_categories():
    frame = TrafficDataAdapter._canonicalize([
        {
            "road_id": 5,
            "vehicle_count": 90,
            "average_speed": 44,
            "timestamp": "2026-09-21T08:15:00",
        },
    ])

    assert frame.iloc[0]["road_id"] == "R005"
