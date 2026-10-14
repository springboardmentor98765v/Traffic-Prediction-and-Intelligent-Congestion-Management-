from fastapi.testclient import TestClient
from Api.traffic_api import app


client = TestClient(app)


# ---------------------------------------------------------
# DAY 6 - M3 ANALYTICS SERVICE TESTS
# ---------------------------------------------------------


def test_trends_day():
    """
    Verify that the trends endpoint returns successful
    daily trend data for a valid road.
    """

    response = client.get(
        "/analytics/trends",
        params={
            "road_id": 1,
            "range": "day"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_trends_week():
    """
    Verify weekly trend analysis.
    """

    response = client.get(
        "/analytics/trends",
        params={
            "road_id": 1,
            "range": "week"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_trends_invalid_range():
    """
    Invalid trend range should be rejected.
    """

    response = client.get(
        "/analytics/trends",
        params={
            "road_id": 1,
            "range": "abc"
        }
    )

    assert response.status_code == 400


# ---------------------------------------------------------
# HEATMAP
# ---------------------------------------------------------


def test_heatmap_week_hour():
    """
    Verify weekly heatmap data using hourly buckets.
    """

    response = client.get(
        "/analytics/heatmap",
        params={
            "road_id": 1,
            "range": "week",
            "bucket": "hour"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_heatmap_day_hour():
    """
    Verify daily heatmap data using hourly buckets.
    """

    response = client.get(
        "/analytics/heatmap",
        params={
            "road_id": 1,
            "range": "day",
            "bucket": "hour"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_heatmap_day_bucket():
    """
    Verify heatmap using daily aggregation.
    """

    response = client.get(
        "/analytics/heatmap",
        params={
            "road_id": 1,
            "range": "day",
            "bucket": "day"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None

# ---------------------------------------------------------
# HISTORICAL REPORT - JSON
# ---------------------------------------------------------


def test_historical_report_json():
    """
    Verify historical traffic report in JSON format.

    The JSON report is intentionally returned as a small
    paginated preview so that Swagger/API remains responsive.
    """

    response = client.get(
        "/analytics/reports",
        params={
            "road_id": 1,
            "range": "week",
            "format": "json",
            "page": 1,
            "page_size": 25
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    # Basic report metadata
    assert data["report_type"] == "historical_traffic"
    assert data["range"] == "week"
    assert data["road_id"] == 1

    # The API intentionally identifies JSON output as a preview
    assert data["format"] == "json_preview"

    # Pagination metadata
    assert "page" in data
    assert "page_size" in data
    assert "returned_records" in data
    assert "has_more" in data

    # Actual report records
    assert "data" in data
    assert isinstance(data["data"], list)

    # Returned record count must match the data actually returned
    assert data["returned_records"] == len(data["data"])

    # Requested page size must be respected
    assert data["page"] == 1
    assert data["page_size"] == 25

    # A page cannot contain more records than requested
    assert data["returned_records"] <= data["page_size"]