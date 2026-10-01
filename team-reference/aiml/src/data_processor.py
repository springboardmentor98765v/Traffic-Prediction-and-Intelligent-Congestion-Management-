import pandas as pd
from congestion import calculate_congestion


def process_traffic_data(file_path):
    df = pd.read_csv(file_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["congestion_level"] = df["average_speed"].apply(
        calculate_congestion
    )

    df["hour"] = df["timestamp"].dt.hour

    return df


if __name__ == "__main__":
    file_path = "../data/raw/traffic_data.csv"

    df = process_traffic_data(file_path)

    print(df)

    df.to_csv(
        "../data/processed/processed_traffic.csv",
        index=False
    )

    print("\nProcessed traffic data saved successfully.")