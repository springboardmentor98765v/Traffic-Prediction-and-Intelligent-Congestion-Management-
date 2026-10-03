import time

from src.ai_engine.anomaly_detector import detect_anomalies
from src.ai_engine.predictor import (
    predict_traffic,
    get_traffic_condition,
)
from src.ai_engine.recommendation_engine import generate_recommendations
from src.route_analysis import (
    analyze_routes,
    rank_routes_with_congestion,
)


# ============================================================
# M2 TESTS
# ============================================================

def test_traffic_prediction():
    result = predict_traffic(
        junction=1,
        hour=8,
        day_of_week=1,
        month=11,
    )

    assert isinstance(result, (int, float))
    assert result >= 0

    print("\nTraffic prediction test: PASS")


def test_traffic_condition():
    result = get_traffic_condition(28.98)

    assert result in [
        "Low Traffic",
        "Medium Traffic",
        "High Traffic",
    ]

    print("\nTraffic condition test: PASS")


def test_route_analysis():
    routes = analyze_routes(
        17.3850,
        78.4867,
        17.4065,
        78.4772,
    )

    assert isinstance(routes, list)
    assert len(routes) > 0

    print("\nRoute analysis test: PASS")


def test_congestion_route_ranking():
    routes = analyze_routes(
        17.3850,
        78.4867,
        17.4065,
        78.4772,
    )

    ranked_routes = rank_routes_with_congestion(
        routes,
        [1, 2],
        8,
        1,
        11,
    )

    assert isinstance(ranked_routes, list)
    assert len(ranked_routes) > 0

    for route in ranked_routes:
        assert "rank" in route
        assert "predicted_vehicle_count" in route
        assert "traffic_condition" in route

    print("\nCongestion route ranking test: PASS")


# ============================================================
# M3 - ANOMALY DETECTION TESTS
# ============================================================

def test_anomaly_detection():
    result = detect_anomalies(
        threshold_std=3.0,
        max_results=10,
    )

    assert isinstance(result, dict)
    assert "anomalies" in result

    print("\nAnomaly detection test: PASS")


def test_anomaly_result_structure():
    result = detect_anomalies(
        threshold_std=3.0,
        max_results=10,
    )

    assert isinstance(result, dict)
    assert "anomalies" in result

    anomalies = result["anomalies"]

    assert isinstance(anomalies, list)

    if anomalies:
        anomaly = anomalies[0]

        assert "road_id" in anomaly
        assert "time" in anomaly
        assert "expected_level" in anomaly
        assert "observed_level" in anomaly
        assert "flagged_as" in anomaly

    print("\nAnomaly result structure test: PASS")


# ============================================================
# M3 - RECOMMENDATION TESTS
# ============================================================

def test_recommendation_generation():
    recommendations = generate_recommendations(1)

    assert isinstance(recommendations, list)

    print("\nRecommendation generation test: PASS")


def test_recommendation_structure():
    recommendations = generate_recommendations(1)

    assert isinstance(recommendations, list)

    if recommendations:
        recommendation = recommendations[0]

        assert "recommendation_text" in recommendation
        assert "based_on" in recommendation

    print("\nRecommendation structure test: PASS")


# ============================================================
# M3 - LATENCY TESTS
# ============================================================

def test_anomaly_detection_latency():
    start_time = time.perf_counter()

    result = detect_anomalies(
        threshold_std=3.0,
        max_results=10,
    )

    end_time = time.perf_counter()

    latency = end_time - start_time

    assert isinstance(result, dict)
    assert latency >= 0

    print("\nAnomaly detection latency:")
    print(f"{latency:.4f} seconds")


def test_recommendation_latency():
    start_time = time.perf_counter()

    result = generate_recommendations(1)

    end_time = time.perf_counter()

    latency = end_time - start_time

    assert isinstance(result, list)
    assert latency >= 0

    print("\nRecommendation generation latency:")
    print(f"{latency:.4f} seconds")


# ============================================================
# M3 - ANOMALY THRESHOLD VALIDATION
# ============================================================

def test_anomaly_threshold_validation():
    result = detect_anomalies(
        threshold_std=3.0,
        max_results=20,
    )

    # The detector returns the calculated traffic threshold,
    # not the threshold_std input value itself.
    assert isinstance(result["threshold"], (int, float))
    assert result["threshold"] > 0

    print("\nAnomaly threshold validation: PASS")


# ============================================================
# M3 - RECOMMENDATION ROAD VALIDATION
# ============================================================

def test_recommendation_road_validation():
    recommendations = generate_recommendations(1)

    assert isinstance(recommendations, list)

    for recommendation in recommendations:
        assert isinstance(recommendation, dict)
        assert "recommendation_text" in recommendation

    print("\nRecommendation road validation: PASS")


# ============================================================
# M3 - COMPLETE AI INSIGHTS VALIDATION
# ============================================================

def test_ai_insights_complete():
    anomalies = detect_anomalies(
        threshold_std=3.0,
        max_results=10,
    )

    recommendations = generate_recommendations(1)

    assert isinstance(anomalies, dict)
    assert isinstance(anomalies.get("anomalies"), list)

    assert isinstance(recommendations, list)

    print("\nComplete AI Insights validation: PASS")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("M3 AI FEATURES TEST SUITE")
    print("=" * 60)

    print("\nRunning tests with pytest...")