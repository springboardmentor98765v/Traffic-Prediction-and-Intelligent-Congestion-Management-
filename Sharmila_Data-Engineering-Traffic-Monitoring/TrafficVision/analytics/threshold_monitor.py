import pandas as pd

# Input and output files
DATA_FILE = "traffic_history_clean.csv"
OUTPUT_FILE = "alerts.csv"

# Data-derived congestion threshold
CONGESTION_THRESHOLD = 0.70


def check_congestion_threshold():

    # Load traffic data
    df = pd.read_csv(DATA_FILE)

    # Find records where density reaches or exceeds the threshold
    alerts = df[df["density"] >= CONGESTION_THRESHOLD].copy()

    # Create alert type
    alerts["alert_type"] = "congestion"

    # Create alert message
    alerts["message"] = alerts["road_id"].apply(
        lambda road: f"High congestion detected on Road {int(road)}"
    )

    # Select required columns
    alerts = alerts[
        [
            "road_id",
            "timestamp",
            "density",
            "congestion_level",
            "alert_type",
            "message"
        ]
    ]

    # Save detected alerts
    alerts.to_csv(OUTPUT_FILE, index=False)

    # Display results
    print("Congestion Threshold:", CONGESTION_THRESHOLD)
    print("Total records:", len(df))
    print("Threshold breaches:", len(alerts))
    print("Alerts saved to:", OUTPUT_FILE)

    print("\nFirst 5 alerts:")
    print(alerts.head().to_string(index=False))


if __name__ == "__main__":
    check_congestion_threshold()