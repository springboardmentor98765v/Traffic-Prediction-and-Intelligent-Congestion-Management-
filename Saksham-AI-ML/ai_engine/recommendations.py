"""
Milestone 3 — Day 4
AI-based traffic recommendation logic.
"""


def generate_recommendation(
    predicted_level,
    estimated_delay_minutes=0,
    trend_congestion=None
):
    """
    Generate a simple and explainable traffic recommendation.
    """

    predicted_level = predicted_level.upper()

    if predicted_level == "SEVERE":
        recommendation = (
            "High congestion is expected. "
            "Consider travelling before the peak period or using an alternate route."
        )

    elif predicted_level == "HIGH":
        recommendation = (
            "High traffic is expected. "
            "Consider travelling earlier or allowing extra travel time."
        )

    elif predicted_level == "MEDIUM":
        recommendation = (
            "Moderate congestion is expected. "
            "Consider allowing some additional travel time."
        )

    else:
        recommendation = "Traffic conditions are expected to be normal."

    if estimated_delay_minutes >= 20:
        recommendation += " Significant delay is expected."

    return {
        "recommendation_text": recommendation,
        "based_on": {
            "predicted_level": predicted_level,
            "estimated_delay_minutes": estimated_delay_minutes,
            "historical_trend_available": trend_congestion is not None,
        },
    }