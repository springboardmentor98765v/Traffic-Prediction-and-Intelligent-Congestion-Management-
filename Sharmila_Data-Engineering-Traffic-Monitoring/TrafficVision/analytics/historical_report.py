import pandas as pd

DATA_FILE = "traffic_history_clean.csv"


def load_data():
    """Load historical traffic data."""

    df = pd.read_csv(DATA_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def generate_report(df, report_range):
    """Generate a historical report for the requested range."""

    if report_range == "day":

        # Keep daily data
        report = df.copy()

    elif report_range == "week":

        # Add week information
        df = df.copy()

        df["week"] = df["timestamp"].dt.to_period("W").apply(
            lambda x: x.start_time.date()
        )

        report = df.copy()

    else:
        raise ValueError(
            "Invalid range. Use 'day' or 'week'."
        )

    return report


if __name__ == "__main__":

    df = load_data()

    # Generate daily report
    daily_report = generate_report(df, "day")

    daily_report.to_csv(
        "historical_traffic_daily.csv",
        index=False
    )

    # Generate weekly report
    weekly_report = generate_report(df, "week")

    weekly_report.to_csv(
        "historical_traffic_weekly.csv",
        index=False
    )

    print("HISTORICAL TRAFFIC REPORTS")
    print("==========================")

    print(
        "\nDaily report records:",
        len(daily_report)
    )

    print(
        "Weekly report records:",
        len(weekly_report)
    )

    print(
        "\nDaily report saved to:",
        "historical_traffic_daily.csv"
    )

    print(
        "Weekly report saved to:",
        "historical_traffic_weekly.csv"
    )