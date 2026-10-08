"""TC-AN-01..17: Analytics Service (Intern 2, M3 Day 5 build) against the live stack.

Contract (frozen by Intern 2 on 2026-09-25, see QA/milestone3/day2/day2_summary.md):
  GET /analytics/trends?road_id=&start_date=&end_date=
  GET /analytics/heatmap?start_date=&end_date=&time_bucket=hour|day
  GET /analytics/reports?road_id=&start_date=&end_date=&limit=   (CSV)
Redis cache, 60 s TTL, keys `analytics:<endpoint>:<sha256>`.

Accuracy oracle: the raw rows from /analytics/reports (separate code path, same
traffic_history table), re-aggregated here in Python on IST days/hours.
Needs Data loaded: bash QA/milestone3/day6/analytics_setup.sh
"""

import csv
import io
import json
import os
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

import pytest

pytestmark = [pytest.mark.live, pytest.mark.analytics]

AN = os.getenv("M3_ANALYTICS_URL", "http://127.0.0.1:8001").rstrip("/")
IST = ZoneInfo("Asia/Kolkata")
DAY = "2026-08-01"
# DEF-M3-009/010/011 fixed and verified 2026-09-26; their tests are now plain passes.


def get(path):
    try:
        with urllib.request.urlopen(AN + path, timeout=30) as resp:
            return resp.status, resp.headers, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read().decode()


def get_json(path):
    status, _, body = get(path)
    assert status == 200, body
    return json.loads(body)


@pytest.fixture(scope="module", autouse=True)
def analytics_up():
    try:
        urllib.request.urlopen(AN + "/", timeout=3)
    except OSError:
        pytest.skip(f"analytics service not reachable at {AN}")


@pytest.fixture(scope="module")
def raw_rows():
    status, _, body = get("/analytics/reports?limit=50000")
    assert status == 200
    rows = list(csv.DictReader(io.StringIO(body)))
    for r in rows:
        r["ist"] = datetime.fromisoformat(r["reading_timestamp"]).astimezone(IST)
    return rows


def avg(values):
    # Postgres ROUND(numeric) is half-up; Python's round() is half-even.
    mean = Decimal(sum(values)) / Decimal(len(values))
    return float(mean.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# --- Trends ---------------------------------------------------------------


def test_tc_an_01_trends_daily_series_is_ordered_and_complete():
    body = get_json("/analytics/trends?road_id=R001")
    days = [d["time_period"] for d in body["daily_trends"]]
    assert days == sorted(days)
    assert len(days) == len(set(days)) == 28
    assert len(body["weekly_pattern"]) == 7 * 24


def test_tc_an_02_trends_daily_values_match_raw_rows(raw_rows):
    body = get_json("/analytics/trends?road_id=R002")
    by_day = defaultdict(list)
    for r in raw_rows:
        if r["road_id"] == "R002":
            by_day[r["ist"].date().isoformat()].append(r)
    for point in body["daily_trends"]:
        rows = by_day[point["time_period"]]
        assert point["total_readings"] == len(rows)
        assert point["avg_vehicle_count"] == pytest.approx(
            avg([int(r["vehicle_count"]) for r in rows]), abs=0.01
        )
        assert point["max_vehicle_count"] == max(int(r["vehicle_count"]) for r in rows)


def test_tc_an_03_trends_date_filter_is_inclusive():
    body = get_json("/analytics/trends?road_id=R001&start_date=2026-08-01&end_date=2026-08-03")
    assert [d["time_period"] for d in body["daily_trends"]] == [
        "2026-08-01",
        "2026-08-02",
        "2026-08-03",
    ]


def test_tc_an_04_trends_requires_road_id():
    assert get("/analytics/trends")[0] == 422


def test_tc_an_05_trends_unknown_road_is_404():
    assert get("/analytics/trends?road_id=R999")[0] == 404


def test_tc_an_06_inverted_date_range_is_rejected():
    assert get("/analytics/trends?road_id=R001&start_date=2026-08-20&end_date=2026-08-01")[0] in (
        400,
        422,
    )


@pytest.mark.parametrize(
    "path",
    [
        "/analytics/trends?road_id=R001&start_date=abc",
        "/analytics/heatmap?start_date=2026-13-45",
        "/analytics/reports?start_date=notadate",
    ],
)
def test_tc_an_07_malformed_date_is_4xx_not_500(path):
    assert get(path)[0] in (400, 422)


# --- Heatmap --------------------------------------------------------------


def test_tc_an_08_heatmap_hour_grid_is_complete():
    body = get_json("/analytics/heatmap?time_bucket=hour")
    assert len(body["roads"]) == 6 and len(body["time_buckets"]) == 24
    cells = {(c["road_id"], c["time_bucket"]) for c in body["grid"]}
    assert len(cells) == len(body["grid"]) == 6 * 24


def test_tc_an_09_heatmap_hour_cells_match_raw_rows(raw_rows):
    body = get_json("/analytics/heatmap?time_bucket=hour")
    cells = defaultdict(list)
    for r in raw_rows:
        cells[(r["road_id"], r["ist"].hour)].append(r)
    for c in body["grid"]:
        rows = cells[(c["road_id"], c["time_bucket"])]
        assert c["total_readings"] == len(rows)
        assert c["avg_vehicle_count"] == pytest.approx(
            avg([int(r["vehicle_count"]) for r in rows]), abs=0.01
        )
        assert (
            c["low_count"] + c["medium_count"] + c["high_count"] + c["severe_count"]
            == c["total_readings"]
        )


def test_tc_an_10_heatmap_day_bucket_matches_trends():
    heat = get_json(f"/analytics/heatmap?time_bucket=day&start_date={DAY}&end_date={DAY}")
    trend = get_json(f"/analytics/trends?road_id=R001&start_date={DAY}&end_date={DAY}")
    cell = next(c for c in heat["grid"] if c["road_id"] == "R001")
    point = trend["daily_trends"][0]
    assert cell["total_readings"] == point["total_readings"]
    assert cell["avg_vehicle_count"] == pytest.approx(point["avg_vehicle_count"], abs=0.01)


def test_tc_an_11_heatmap_rejects_unknown_bucket():
    assert get("/analytics/heatmap?time_bucket=week")[0] == 400


# --- Reports --------------------------------------------------------------


def test_tc_an_12_report_is_csv_download_with_row_count():
    status, headers, body = get("/analytics/reports?road_id=R001&limit=5")
    assert status == 200
    assert headers["content-type"].startswith("text/csv")
    assert 'filename="traffic_historical_report_R001.csv"' in headers["content-disposition"]
    rows = list(csv.DictReader(io.StringIO(body)))
    assert len(rows) == int(headers["x-report-row-count"]) == 5
    assert {r["road_id"] for r in rows} == {"R001"}


@pytest.mark.parametrize("limit", [0, 50001])
def test_tc_an_13_report_limit_bounds(limit):
    assert get(f"/analytics/reports?limit={limit}")[0] == 400


def test_tc_an_14_report_day_matches_trends_day():
    _, _, body = get(f"/analytics/reports?road_id=R001&start_date={DAY}&end_date={DAY}")
    rows = list(csv.DictReader(io.StringIO(body)))
    days = {
        datetime.fromisoformat(r["reading_timestamp"]).astimezone(IST).date().isoformat()
        for r in rows
    }
    assert days == {DAY}


# --- Caching --------------------------------------------------------------


@pytest.fixture
def redis_client():
    redis = pytest.importorskip("redis")
    client = redis.Redis(
        host=os.getenv("M3_REDIS_HOST", "127.0.0.1"), port=6379, decode_responses=True
    )
    try:
        client.ping()
    except redis.exceptions.ConnectionError:
        pytest.skip("redis not reachable from host")
    for key in client.scan_iter("analytics:*"):
        client.delete(key)
    return client


@pytest.mark.parametrize(
    "endpoint,path",
    [
        ("trends", "/analytics/trends?road_id=R003"),
        ("heatmap", "/analytics/heatmap?time_bucket=day"),
    ],
)
def test_tc_an_15_response_is_cached_with_60s_ttl(redis_client, endpoint, path):
    first = get_json(path)
    keys = list(redis_client.scan_iter(f"analytics:{endpoint}:*"))
    assert len(keys) == 1
    assert 0 < redis_client.ttl(keys[0]) <= 60
    assert get_json(path) == first
    assert json.loads(redis_client.get(keys[0])) == first


def test_tc_an_16_different_params_use_different_keys(redis_client):
    get_json("/analytics/trends?road_id=R001")
    get_json("/analytics/trends?road_id=R002")
    assert len(list(redis_client.scan_iter("analytics:trends:*"))) == 2


def test_tc_an_17_four_week_queries_uncached_under_2s(redis_client):
    for path in (
        "/analytics/heatmap?time_bucket=hour",
        "/analytics/heatmap?time_bucket=day",
        "/analytics/trends?road_id=R004",
        "/analytics/reports?limit=50000",
    ):
        for key in redis_client.scan_iter("analytics:*"):
            redis_client.delete(key)
        start = time.perf_counter()
        assert get(path)[0] == 200
        assert time.perf_counter() - start < 2.0, path
