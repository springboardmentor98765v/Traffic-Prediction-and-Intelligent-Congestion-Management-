import pandas as pd
import json

# Input dataset
DATA_FILE = "traffic_history_clean.csv"


def load_data():
    """Load and prepare traffic data."""

    df = pd.read_csv(DATA_FILE)

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def generate_daily_trends(df):
    """Generate average daily congestion for each road."""

    data = df.copy()

    data["date"] = data["timestamp"].dt.date

    daily_trends = (
        data.groupby(["road_id", "date"])["density"]
        .mean()
        .reset_index()
    )

    daily_trends = daily_trends.rename(
        columns={"density": "avg_congestion"}
    )

    daily_trends["avg_congestion"] = (
        daily_trends["avg_congestion"].round(3)
    )

    return daily_trends


def generate_weekly_trends(df):
    """Generate average weekly congestion for each road."""

    data = df.copy()

    data["week"] = data["timestamp"].dt.to_period("W").apply(
        lambda x: x.start_time.date()
    )

    weekly_trends = (
        data.groupby(["road_id", "week"])["density"]
        .mean()
        .reset_index()
    )

    weekly_trends = weekly_trends.rename(
        columns={"density": "avg_congestion"}
    )

    weekly_trends["avg_congestion"] = (
        weekly_trends["avg_congestion"].round(3)
    )

    return weekly_trends


def create_daily_output(daily_trends, road_id):
    """Create SRS-style daily trend output for one road."""

    road_data = daily_trends[
        daily_trends["road_id"] == road_id
    ]

    points = []

    for _, row in road_data.iterrows():

        points.append({
            "period": str(row["date"]),
            "avg_congestion": float(row["avg_congestion"])
        })

    return {
        "road_id": int(road_id),
        "points": points
    }


def create_weekly_output(weekly_trends, road_id):
    """Create SRS-style weekly trend output for one road."""

    road_data = weekly_trends[
        weekly_trends["road_id"] == road_id
    ]

    points = []

    for _, row in road_data.iterrows():

        points.append({
            "period": str(row["week"]),
            "avg_congestion": float(row["avg_congestion"])
        })

    return {
        "road_id": int(road_id),
        "points": points
    }


if __name__ == "__main__":

    # Load data
    df = load_data()

    # Generate trends
    daily = generate_daily_trends(df)
    weekly = generate_weekly_trends(df)

    # Create output for Road 1
    daily_output = create_daily_output(daily, 1)
    weekly_output = create_weekly_output(weekly, 1)

    print("DAILY TREND OUTPUT - ROAD 1")
    print("==========================")
    print(json.dumps(daily_output, indent=4))

    print("\n\nWEEKLY TREND OUTPUT - ROAD 1")
    print("===========================")
    print(json.dumps(weekly_output, indent=4))