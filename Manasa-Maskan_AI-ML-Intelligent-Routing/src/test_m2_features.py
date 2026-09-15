from src.ai_engine.predictor import (
    predict_traffic,
    get_traffic_condition,
)

from src.route_analysis import (
    analyze_routes,
    rank_routes_with_congestion,
)


def test_traffic_prediction():
    prediction = predict_traffic(
        junction=1,
        hour=8,
        day_of_week=1,
        month=11,
    )

    assert isinstance(prediction, float)
    assert prediction >= 0


def test_traffic_condition():
    assert get_traffic_condition(5) == "Low Traffic"
    assert get_traffic_condition(15) == "Medium Traffic"
    assert get_traffic_condition(30) == "High Traffic"


def test_route_analysis():
    routes = analyze_routes(
        17.3850,
        78.4867,
        17.4065,
        78.4772,
    )

    assert len(routes) >= 1

    for route in routes:
        assert "route_id" in route
        assert "distance_km" in route
        assert "estimated_minutes" in route


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

    assert len(ranked_routes) >= 1

    for route in ranked_routes:
        assert "predicted_vehicle_count" in route
        assert "traffic_condition" in route
        assert "estimated_delay_minutes" in route
        assert "rank" in route