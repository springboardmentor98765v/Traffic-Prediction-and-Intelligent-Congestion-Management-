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


def generate_heatmap(df):
    """Generate road × time-bucket heatmap data."""

    data = df.copy()

    # Extract hour as the time bucket
    data["hour"] = data["timestamp"].dt.hour

    # Calculate average density for each road and hour
    heatmap = (
        data.groupby(["road_id", "hour"])["density"]
        .mean()
        .reset_index()
    )

    # Round density values
    heatmap["density"] = heatmap["density"].round(3)

    # Create road × hour matrix
    matrix = heatmap.pivot(
        index="road_id",
        columns="hour",
        values="density"
    )

    # Make sure hours are in order from 0 to 23
    matrix = matrix.reindex(columns=range(24))

    # Make sure roads are in order
    matrix = matrix.reindex(index=sorted(data["road_id"].unique()))

    return matrix


def create_heatmap_output(matrix):
    """Create SRS-style heatmap output."""

    roads = [int(road) for road in matrix.index]

    time_buckets = [
        f"{hour:02d}:00"
        for hour in matrix.columns
    ]

    values = matrix.values.tolist()

    # Convert values to normal Python floats
    values = [
        [
            round(float(value), 3)
            for value in row
        ]
        for row in values
    ]

    return {
        "roads": roads,
        "time_buckets": time_buckets,
        "values": values
    }


if __name__ == "__main__":

    # Load data
    df = load_data()

    # Generate heatmap matrix
    matrix = generate_heatmap(df)

    # Create output
    heatmap_output = create_heatmap_output(matrix)

    print("TRAFFIC CONGESTION HEATMAP")
    print("==========================")

    print("\nRoads:")
    print(heatmap_output["roads"])

    print("\nTime Buckets:")
    print(heatmap_output["time_buckets"])

    print("\nHeatmap Values:")
    print(json.dumps(heatmap_output["values"], indent=4))