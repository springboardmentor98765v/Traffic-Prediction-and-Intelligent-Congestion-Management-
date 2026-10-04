from src.ai_engine.recommendation_engine import generate_recommendations


def test_generate_recommendations():
    """Test that AI recommendations are generated correctly."""

    road_id = 1

    recommendations = generate_recommendations(road_id)

    # Check that recommendations are returned as a list
    assert isinstance(recommendations, list)

    # Check that at least one recommendation is generated
    assert len(recommendations) > 0

    # Check the structure of every recommendation
    for recommendation in recommendations:
        assert isinstance(recommendation, dict)

        # Required fields
        assert "recommendation_text" in recommendation
        assert "based_on" in recommendation

        # Required fields should contain text
        assert isinstance(
            recommendation["recommendation_text"],
            str,
        )

        assert isinstance(
            recommendation["based_on"],
            str,
        )

        # Values should not be empty
        assert recommendation["recommendation_text"].strip() != ""
        assert recommendation["based_on"].strip() != ""


def test_recommendations_for_valid_road():
    """Test recommendations for another valid road."""

    road_id = 3

    recommendations = generate_recommendations(road_id)

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    for recommendation in recommendations:
        assert "recommendation_text" in recommendation
        assert "based_on" in recommendation