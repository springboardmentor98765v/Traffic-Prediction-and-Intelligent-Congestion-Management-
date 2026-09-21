import pandas as pd

DATA_PATH = "data/processed/processed_traffic.csv"


def run_eda():
    df = pd.read_csv(DATA_PATH)

    print("\n===== TRAFFIC DATASET EDA =====")

    print("\nDataset shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nNumerical statistics:")
    print(df.describe())

    print("\nCongestion distribution:")
    print(df["congestion_level"].value_counts())

    print("\nAverage speed by congestion level:")
    print(
        df.groupby("congestion_level")["average_speed"]
        .mean()
        .sort_values()
    )

    print("\nAverage vehicle count by congestion level:")
    print(
        df.groupby("congestion_level")["vehicle_count"]
        .mean()
        .sort_values()
    )


if __name__ == "__main__":
    run_eda()