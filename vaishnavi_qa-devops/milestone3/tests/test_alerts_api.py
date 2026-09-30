"""TC-AL-10..32 — Alert Service API against the running stack (secured contract).

Contract since the DEF-M3-005/012 fix (retest 2026-09-26): every endpoint needs a JWT and
the role comes from the token, not from ``?role=``. Test alerts are created with an admin
JWT, which the current API accepts. Open defects are strict xfails: they turn red the
moment the fix lands, so they get promoted.
"""

import time

import pytest

pytestmark = pytest.mark.live

ALERTS = "/api/v1/alerts/"
DEF_M3_005 = "DEF-M3-005: any logged-in user may create alerts / mark any alert read"
DEF_M3_016 = "DEF-M3-016: created_at returned without a timezone offset"
DEF_M3_024 = "DEF-M3-024: JWT role is 'PUBLIC' but the filter hides Critical only for 'user'"
DEF_M3_025 = "DEF-M3-025: producer service key (ALERT_SERVICE_KEY) not accepted by the API"


@pytest.fixture(scope="module")
def admin(role_tokens):
    return role_tokens["admin"]


def create(api, road, token, severity="High", type_="congestion", **kw):
    return api.post(
        ALERTS,
        {
            "type": type_,
            "severity": severity,
            "road_id": road,
            "message": f"QA {severity} {type_} on {road}",
        },
        token=token,
        **kw,
    )


def mine(api, token):
    status, body = api.get("/api/v1/alerts/my", token=token)
    assert status == 200
    return body


# --- Contract / functional ------------------------------------------------


def test_tc_al_10_create_returns_201_and_contract_fields(api, admin, unique_road):
    status, body = create(api, unique_road, admin)
    assert status == 201
    assert body["status"] == "created"
    assert body["road_id"] == unique_road
    assert isinstance(body["alert_id"], int)


@pytest.mark.parametrize("missing", ["type", "severity", "road_id", "message"])
def test_tc_al_11_missing_required_field_is_422(api, admin, missing):
    payload = {"type": "congestion", "severity": "High", "road_id": "R001", "message": "m"}
    del payload[missing]
    status, _ = api.post(ALERTS, payload, token=admin)
    assert status == 422


def test_tc_al_12_new_alert_is_listed_unread_with_all_fields(api, admin, unique_road):
    _, created = create(api, unique_road, admin)
    listed = [a for a in mine(api, admin) if a["alert_id"] == created["alert_id"]]
    assert len(listed) == 1
    alert = listed[0]
    assert set(alert) == {
        "alert_id",
        "type",
        "severity",
        "road_id",
        "message",
        "read",
        "created_at",
    }
    assert alert["read"] is False


def test_tc_al_13_list_is_newest_first(api, admin, unique_road):
    _, first = create(api, unique_road, admin)
    _, second = create(api, unique_road, admin)
    ids = [a["alert_id"] for a in mine(api, admin) if a["road_id"] == unique_road]
    assert ids == [second["alert_id"], first["alert_id"]]


def test_tc_al_14_mark_read(api, admin, unique_road):
    _, created = create(api, unique_road, admin)
    status, body = api.patch(f"/api/v1/alerts/{created['alert_id']}/read", token=admin)
    assert status == 200 and body["read"] is True
    alert = next(a for a in mine(api, admin) if a["alert_id"] == created["alert_id"])
    assert alert["read"] is True


def test_tc_al_15_mark_read_unknown_id_is_404(api, admin):
    status, _ = api.patch("/api/v1/alerts/2147483647/read", token=admin)
    assert status == 404


# --- Role-scoped visibility (role from the JWT) ----------------------------


def test_tc_al_16_user_view_hides_critical(api, admin, role_tokens, unique_road):
    create(api, unique_road, admin, severity="Critical", type_="accident")
    assert not [a for a in mine(api, role_tokens["user"]) if a["road_id"] == unique_road]


@pytest.mark.parametrize("role", ["operator", "admin"])
def test_tc_al_17_operator_and_admin_see_critical(api, admin, role_tokens, unique_road, role):
    create(api, unique_road, admin, severity="Critical", type_="accident")
    assert [a for a in mine(api, role_tokens[role]) if a["road_id"] == unique_road]


def test_tc_al_18_user_view_keeps_non_critical(api, admin, role_tokens, unique_road):
    for sev in ("Low", "Medium", "High"):
        create(api, unique_road, admin, severity=sev)
    sevs = {a["severity"] for a in mine(api, role_tokens["user"]) if a["road_id"] == unique_road}
    assert sevs == {"Low", "Medium", "High"}


@pytest.mark.parametrize("severity", ["critical", "Severe", "urgent"])
def test_tc_al_19_severity_outside_vocabulary_is_422(api, admin, unique_road, severity):
    # DEF-M3-008 fix: severity is an Enum (Low/Medium/High/Critical).
    status, _ = create(api, unique_road, admin, severity=severity)
    assert status == 422


# --- Authentication / authorisation ---------------------------------------


def test_tc_al_20_list_requires_authentication(api):
    status, _ = api.get("/api/v1/alerts/my")
    assert status == 401


def test_tc_al_21_public_user_cannot_escalate_via_role_param(api, admin, role_tokens, unique_road):
    create(api, unique_road, admin, severity="Critical", type_="accident")
    status, body = api.get("/api/v1/alerts/my?role=admin", token=role_tokens["user"])
    assert status in (200, 403)
    if status == 200:
        assert not [a for a in body if a["road_id"] == unique_road]


def test_tc_al_22_create_requires_authentication(api, unique_road):
    status, _ = create(api, unique_road, None)
    assert status in (401, 403)


def test_tc_al_23_mark_read_requires_authentication(api, admin, unique_road):
    _, created = create(api, unique_road, admin)
    status, _ = api.patch(f"/api/v1/alerts/{created['alert_id']}/read")
    assert status in (401, 403)


def test_tc_al_29_public_user_cannot_create_alerts(api, role_tokens, unique_road):
    status, _ = create(api, unique_road, role_tokens["user"], severity="Critical")
    assert status == 403


def test_tc_al_30_public_user_cannot_mark_critical_read(api, admin, role_tokens, unique_road):
    _, created = create(api, unique_road, admin, severity="Critical", type_="accident")
    status, _ = api.patch(f"/api/v1/alerts/{created['alert_id']}/read", token=role_tokens["user"])
    assert status in (403, 404)


def test_tc_al_31_producer_service_key_is_accepted(api, service_headers, unique_road):
    assert service_headers, "ALERT_SERVICE_KEY not set in .env.dev"
    status, _ = create(api, unique_road, None, headers=service_headers)
    assert status == 201


def test_tc_al_32_created_at_has_timezone(api, admin, unique_road):
    _, created = create(api, unique_road, admin)
    alert = next(a for a in mine(api, admin) if a["alert_id"] == created["alert_id"])
    stamp = alert["created_at"]
    assert stamp.endswith("Z") or "+" in stamp[10:] or "-" in stamp[19:]


# --- Delivery timing ------------------------------------------------------


def test_tc_al_24_alert_visible_within_2s_of_creation(api, admin, role_tokens, unique_road):
    start = time.perf_counter()
    _, created = create(api, unique_road, admin)
    while time.perf_counter() - start < 2:
        if any(a["alert_id"] == created["alert_id"] for a in mine(api, role_tokens["user"])):
            return
    pytest.fail("alert not visible to a public user within 2 s")
