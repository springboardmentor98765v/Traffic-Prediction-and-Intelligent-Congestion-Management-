import os
import pandas as pd

from .predictor import predict_traffic, get_traffic_condition


# ---------------------------------------------------------
# Project base directory
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )
)


# ---------------------------------------------------------
# Historical traffic dataset
# ---------------------------------------------------------

DATA_PATH = os.path.join(
    BASE_DIR,
    "Sharmila_Data-Engineering-Traffic-Monitoring",
    "TrafficVision",
    "data",
    "traffic.csv",
)


# ---------------------------------------------------------
# Load historical traffic data
# ---------------------------------------------------------

def load_historical_data():
    """
    Load historical traffic data used for
    generating AI-based recommendations.
    """

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Historical traffic dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    df["DateTime"] = pd.to_datetime(df["DateTime"])

    df["hour"] = df["DateTime"].dt.hour

    return df


# ---------------------------------------------------------
# Generate AI traffic recommendations
# ---------------------------------------------------------

def generate_recommendations(road_id: int):
    """
    Generate simple and explainable traffic recommendations.

    Recommendations are based on:
    1. M2 trained traffic prediction model
    2. Historical traffic patterns
    """

    # Load historical traffic data
    df = load_historical_data()

    # -----------------------------------------------------
    # Get data for requested road
    # -----------------------------------------------------

    road_data = df[df["Junction"] == road_id].copy()

    if road_data.empty:
        return [
            {
                "recommendation_text": (
                    f"No historical traffic data is available "
                    f"for road {road_id}."
                ),
                "based_on": "Historical traffic data",
            }
        ]

    # -----------------------------------------------------
    # Calculate average traffic for each hour
    # -----------------------------------------------------

    hourly_average = (
        road_data
        .groupby("hour")["Vehicles"]
        .mean()
        .sort_values()
    )

    # Busiest hour
    busiest_hour = int(hourly_average.idxmax())

    # Quietest hour
    quietest_hour = int(hourly_average.idxmin())

    # Average traffic values
    busiest_traffic = float(hourly_average.max())
    quietest_traffic = float(hourly_average.min())

    # -----------------------------------------------------
    # Use M2 trained model
    # -----------------------------------------------------

    # Example reference time for generating
    # the current traffic recommendation.
    current_hour = 12
    current_day = 1
    current_month = 11

    predicted_current = predict_traffic(
        road_id,
        current_hour,
        current_day,
        current_month,
    )

    current_condition = get_traffic_condition(
        predicted_current
    )

    # -----------------------------------------------------
    # Generate recommendations
    # -----------------------------------------------------

    recommendations = []

    # -----------------------------------------------------
    # High traffic
    # -----------------------------------------------------

    if current_condition == "High Traffic":

        recommendations.append(
            {
                "recommendation_text": (
                    f"Consider travelling outside the current "
                    f"high-traffic period. Historical data shows "
                    f"lower traffic around {quietest_hour}:00, "
                    f"with an average of approximately "
                    f"{quietest_traffic:.1f} vehicles."
                ),
                "based_on": (
                    "M2 traffic prediction and historical "
                    "hourly traffic trend"
                ),
            }
        )

        recommendations.append(
            {
                "recommendation_text": (
                    f"Avoid the busiest period around "
                    f"{busiest_hour}:00 when possible. "
                    f"Historical traffic averages approximately "
                    f"{busiest_traffic:.1f} vehicles during "
                    f"that period."
                ),
                "based_on": (
                    "Historical traffic trend"
                ),
            }
        )

    # -----------------------------------------------------
    # Medium traffic
    # -----------------------------------------------------

    elif current_condition == "Medium Traffic":

        recommendations.append(
            {
                "recommendation_text": (
                    f"Traffic is currently predicted to be "
                    f"moderate. If your schedule is flexible, "
                    f"consider travelling around "
                    f"{quietest_hour}:00 to reduce congestion."
                ),
                "based_on": (
                    "M2 traffic prediction and historical "
                    "hourly traffic trend"
                ),
            }
        )

        recommendations.append(
            {
                "recommendation_text": (
                    f"The historically busiest period is "
                    f"around {busiest_hour}:00."
                ),
                "based_on": (
                    "Historical traffic trend"
                ),
            }
        )

    # -----------------------------------------------------
    # Low traffic
    # -----------------------------------------------------

    else:

        recommendations.append(
            {
                "recommendation_text": (
                    "Traffic is currently predicted to be low. "
                    "Normal travel is recommended."
                ),
                "based_on": (
                    "M2 traffic prediction"
                ),
            }
        )

        recommendations.append(
            {
                "recommendation_text": (
                    f"If possible, avoid the historically "
                    f"busiest period around {busiest_hour}:00."
                ),
                "based_on": (
                    "Historical traffic trend"
                ),
            }
        )

    return recommendations


# ---------------------------------------------------------
# Direct test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("TrafficVision M3 - AI Recommendations")
    print("=" * 50)

    road_id = 1

    print(f"Road ID: {road_id}")
    print()

    result = generate_recommendations(road_id)

    print("Recommendations:")
    print()

    for index, recommendation in enumerate(
        result,
        start=1
    ):
        print(f"{index}. {recommendation['recommendation_text']}")
        print(
            f"   Based on: "
            f"{recommendation['based_on']}"
        )
        print()