from src.ai_engine.recommendation_engine import generate_recommendations


print("=" * 60)
print("DAY 5 - RECOMMENDATION LOGIC TEST")
print("=" * 60)

road_id = 1

recommendations = generate_recommendations(road_id)

print(f"\nRoad ID: {road_id}")
print(f"Total recommendations: {len(recommendations)}")

print("\nRecommendations:")
print("-" * 60)

for index, recommendation in enumerate(
    recommendations,
    start=1
):
    print(f"\nRecommendation {index}")

    print(
        "Text:",
        recommendation.get("recommendation_text")
    )

    print(
        "Based on:",
        recommendation.get("based_on")
    )

print("\n" + "=" * 60)
print("Recommendation logic test completed.")
print("=" * 60)