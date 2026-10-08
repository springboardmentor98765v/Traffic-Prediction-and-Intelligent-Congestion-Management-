"""M1 Traffic Monitoring service (Intern 2) against the frozen contract, SRS section 7.2.

In-process the service has no traffic tables, so it serves its built-in sample feed
(R001-R006). That still exercises the routes, the response shape and the congestion
labels. The live-database path is covered by QA/milestone1/day5/m1_live_stack_check.py.
"""

import pytest

LEVELS = {"Low", "Medium", "High", "Severe"}


@pytest.fixture(scope="module")
def live(client):
    resp = client.get("/api/v1/traffic/live")
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_tc_trf_01_live_returns_non_empty_list(live):
    assert isinstance(live, list) and live


def test_tc_trf_02_live_items_match_contract(live):
    for row in live:
        assert {"road_id", "vehicle_count", "density", "congestion_level", "updated_at"} <= (
            row.keys()
        ), row


def test_tc_trf_03_live_values_are_valid(live):
    for row in live:
        assert row["vehicle_count"] >= 0
        assert row["density"] >= 0
        assert row["congestion_level"] in LEVELS


def test_tc_trf_04_live_road_ids_are_unique(live):
    ids = [row["road_id"] for row in live]
    assert len(ids) == len(set(ids))


def test_tc_trf_05_road_detail_matches_contract(client, live):
    road_id = live[0]["road_id"]
    resp = client.get(f"/api/v1/traffic/road/{road_id}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert {"road_id", "name", "congestion_level", "history"} <= body.keys()
    assert body["road_id"] == road_id
    assert isinstance(body["history"], list) and body["history"]


def test_tc_trf_06_road_detail_agrees_with_live_feed(client, live):
    for row in live:
        detail = client.get(f"/api/v1/traffic/road/{row['road_id']}").json()
        assert detail["congestion_level"] == row["congestion_level"]


def test_tc_trf_07_unknown_road_returns_404(client):
    assert client.get("/api/v1/traffic/road/R999").status_code == 404


def test_tc_trf_08_density_kpis(client, live):
    resp = client.get("/api/v1/traffic/density")
    assert resp.status_code == 200, resp.text
    kpi = resp.json()
    assert {"total_roads", "average_density"} <= kpi.keys()
    assert kpi["total_roads"] == len(live)
    densities = [row["density"] for row in live]
    assert min(densities) <= kpi["average_density"] <= max(densities)


def test_tc_trf_09_congestion_rule_thresholds():
    """Intern 2's threshold rule: vehicle_count / road_capacity."""
    from congestion_calculator import calculate_congestion

    assert calculate_congestion(40, 100) == "Low"
    assert calculate_congestion(50, 100) == "Medium"
    assert calculate_congestion(80, 100) == "Medium"
    assert calculate_congestion(90, 100) == "High"
    assert calculate_congestion(120, 100) == "Severe"
    with pytest.raises(ValueError):
        calculate_congestion(10, 0)
