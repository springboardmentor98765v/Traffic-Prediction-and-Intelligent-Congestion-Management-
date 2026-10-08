from pathlib import Path


def test_day5_sql_exists():
    assert Path(
        "sql/m2_day5_aggregation.sql"
    ).exists()


def test_hourly_generator_exists():
    assert Path(
        "src/generate_traffic_aggregates.py"
    ).exists()


def test_hourly_metrics_table_is_referenced():
    sql = Path(
        "sql/m2_day5_aggregation.sql"
    ).read_text(encoding="utf-8")

    assert "hourly_metrics_road_time" in sql


def test_daily_metrics_table_is_referenced():
    sql = Path(
        "sql/m2_day5_aggregation.sql"
    ).read_text(encoding="utf-8")

    assert "daily_metrics_road_date" in sql


def test_generator_contains_hourly_aggregation():
    source = Path(
        "src/generate_traffic_aggregates.py"
    ).read_text(encoding="utf-8")

    assert "hourly_traffic_metrics" in source
    assert "date_trunc('hour'" in source


def test_generator_contains_daily_aggregation():
    source = Path(
        "src/generate_traffic_aggregates.py"
    ).read_text(encoding="utf-8")

    assert "daily_traffic_metrics" in source
    assert "DATE(reading_timestamp)" in source