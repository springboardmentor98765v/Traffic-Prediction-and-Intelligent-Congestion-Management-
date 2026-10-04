from src.ai_engine.anomaly_detector import detect_anomalies


def test_detect_anomalies():
    """Test that the anomaly detector returns valid anomaly results."""

    result = detect_anomalies(
        threshold_std=3.0,
        max_results=10,
    )

    # Result should be a dictionary
    assert isinstance(result, dict)

    # Required result fields
    assert "threshold" in result
    assert "total_anomalies" in result
    assert "anomalies" in result

    # Threshold should be a positive number
    assert result["threshold"] > 0

    # Total anomalies should be a non-negative integer
    assert isinstance(result["total_anomalies"], int)
    assert result["total_anomalies"] >= 0

    # Anomalies should be returned as a list
    assert isinstance(result["anomalies"], list)

    # We requested a maximum of 10 results
    assert len(result["anomalies"]) <= 10


def test_anomaly_record_structure():
    """Test the structure of detected anomaly records."""

    result = detect_anomalies(
        threshold_std=3.0,
        max_results=10,
    )

    anomalies = result["anomalies"]

    # If anomalies are detected, verify their structure
    for anomaly in anomalies:
        assert isinstance(anomaly, dict)

        assert "road_id" in anomaly
        assert "time" in anomaly
        assert "expected_level" in anomaly
        assert "observed_level" in anomaly
        assert "flagged_as" in anomaly

        assert anomaly["flagged_as"] == "possible_incident"