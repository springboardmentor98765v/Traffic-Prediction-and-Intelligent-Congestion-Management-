from ai_engine.anomaly_detection import detect_anomaly
from ai_engine.recommendations import generate_recommendation


# M3 Day 6: Anomaly Detection Tests

def test_anomaly_medium_to_severe():
    assert detect_anomaly("MEDIUM", "SEVERE") is True


def test_anomaly_medium_to_high():
    assert detect_anomaly("MEDIUM", "HIGH") is False


def test_anomaly_low_to_severe():
    assert detect_anomaly("LOW", "SEVERE") is True


def test_anomaly_same_level():
    assert detect_anomaly("HIGH", "HIGH") is False


# M3 Day 6: Recommendation Tests

def test_recommendation_low():
    result = generate_recommendation("LOW", 0)

    assert "normal" in result["recommendation_text"].lower()


def test_recommendation_high():
    result = generate_recommendation("HIGH", 10)

    assert "earlier" in result["recommendation_text"].lower()


def test_recommendation_severe():
    result = generate_recommendation("SEVERE", 25)

    assert "alternate route" in result["recommendation_text"].lower()


def test_recommendation_significant_delay():
    result = generate_recommendation("HIGH", 20)

    assert "significant delay" in result["recommendation_text"].lower()