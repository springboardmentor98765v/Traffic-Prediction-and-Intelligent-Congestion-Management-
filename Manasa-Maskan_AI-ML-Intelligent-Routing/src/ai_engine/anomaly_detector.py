from pathlib import Path

import joblib
import pandas as pd


# =========================================================
# PROJECT PATHS
# =========================================================

# Project folder:
# Manasa-Maskan_AI-ML-Intelligent-Routing
BASE_DIR = Path(__file__).resolve().parents[2]

# M2 trained Random Forest model
MODEL_PATH = BASE_DIR / "src" / "m2_traffic_model.pkl"

# Sharmila's traffic dataset
# Sharmila's folder is outside the Manasa folder,
# so we use BASE_DIR.parent.
DATA_PATH = (
    BASE_DIR.parent
    / "Sharmila_Data-Engineering-Traffic-Monitoring"
    / "TrafficVision"
    / "data"
    / "traffic.csv"
)


# =========================================================
# TRAFFIC LEVEL
# =========================================================

def get_traffic_level(vehicle_count):
    """
    Convert predicted/observed vehicle count
    into a simple traffic level.
    """

    if vehicle_count < 10:
        return "Low"
    elif vehicle_count < 25:
        return "Medium"
    else:
        return "High"


# =========================================================
# LOAD TRAINED MODEL
# =========================================================

def load_model():
    """
    Load the trained M2 Random Forest model.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


# =========================================================
# LOAD TRAFFIC DATA
# =========================================================

def load_traffic_data():
    """
    Load historical traffic data and create
    the same features used by the M2 model.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Traffic dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    # Convert DateTime column
    df["DateTime"] = pd.to_datetime(df["DateTime"])

    # Feature engineering
    df["hour"] = df["DateTime"].dt.hour
    df["day_of_week"] = df["DateTime"].dt.dayofweek
    df["month"] = df["DateTime"].dt.month

    return df


# =========================================================
# CALCULATE MODEL PREDICTIONS
# =========================================================

def add_predictions(df, model):
    """
    Generate expected traffic using the M2 model.
    """

    features = [
        "Junction",
        "hour",
        "day_of_week",
        "month",
    ]

    df["predicted_vehicles"] = model.predict(
        df[features]
    )

    # Difference between actual and predicted traffic
    df["residual"] = (
        df["Vehicles"]
        - df["predicted_vehicles"]
    )

    return df


# =========================================================
# CALCULATE ANOMALY THRESHOLD
# =========================================================

def calculate_anomaly_threshold(df, threshold_std=2.0):
    """
    Calculate a statistical threshold using
    historical prediction errors.

    A large positive residual means the observed
    traffic is much higher than expected.
    """

    absolute_residuals = df["residual"].abs()

    mean_error = absolute_residuals.mean()
    std_error = absolute_residuals.std()

    threshold = (
        mean_error
        + threshold_std * std_error
    )

    return float(threshold)


# =========================================================
# DETECT ANOMALIES
# =========================================================

def detect_anomalies(
    threshold_std=2.0,
    max_results=20
):
    """
    Detect unusual traffic patterns.

    If observed traffic is significantly higher
    than predicted traffic, it is flagged as
    a possible incident.
    """

    # Load model and data
    model = load_model()
    df = load_traffic_data()

    # Generate predictions
    df = add_predictions(df, model)

    # Calculate threshold
    anomaly_threshold = calculate_anomaly_threshold(
        df,
        threshold_std
    )

    # Detect unusually high traffic
    anomaly_df = df[
        df["residual"] > anomaly_threshold
    ].copy()

    # Calculate anomaly score
    anomaly_df["anomaly_score"] = (
        anomaly_df["residual"]
        / anomaly_threshold
    )

    # Strongest anomalies first
    anomaly_df = anomaly_df.sort_values(
        "anomaly_score",
        ascending=False
    )

    results = []

    for _, row in anomaly_df.head(
        max_results
    ).iterrows():

        results.append(
            {
                "road_id": int(
                    row["Junction"]
                ),

                "time": row[
                    "DateTime"
                ].isoformat(),

                "expected_vehicles": round(
                    float(
                        row[
                            "predicted_vehicles"
                        ]
                    ),
                    2
                ),

                "observed_vehicles": int(
                    row["Vehicles"]
                ),

                "expected_level":
                    get_traffic_level(
                        row[
                            "predicted_vehicles"
                        ]
                    ),

                "observed_level":
                    get_traffic_level(
                        row["Vehicles"]
                    ),

                "residual": round(
                    float(
                        row["residual"]
                    ),
                    2
                ),

                "anomaly_score": round(
                    float(
                        row[
                            "anomaly_score"
                        ]
                    ),
                    2
                ),

                "flagged_as":
                    "possible_incident",
            }
        )

    return {
        "threshold": round(
            anomaly_threshold,
            2
        ),

        "total_anomalies": int(
            len(anomaly_df)
        ),

        "anomalies": results,
    }


# =========================================================
# DETECT ANOMALY FOR A SPECIFIC ROAD
# =========================================================

def detect_road_anomaly(road_id):
    """
    Check the latest traffic record
    for a particular road/junction.
    """

    model = load_model()
    df = load_traffic_data()

    # Select requested road
    road_data = df[
        df["Junction"] == road_id
    ].copy()

    if road_data.empty:
        return {
            "road_id": road_id,
            "status": "no_data",
            "message":
                "No traffic data found "
                "for this road.",
        }

    # Generate predictions
    road_data = add_predictions(
        road_data,
        model
    )

    # Calculate threshold using
    # the complete dataset
    full_df = add_predictions(
        df.copy(),
        model
    )

    anomaly_threshold = (
        calculate_anomaly_threshold(
            full_df,
            threshold_std=2.0
        )
    )

    # Get latest record
    latest = road_data.sort_values(
        "DateTime"
    ).iloc[-1]

    # Determine whether it is anomalous
    is_anomaly = (
        latest["residual"]
        > anomaly_threshold
    )

    if is_anomaly:
        flag = "possible_incident"
    else:
        flag = "normal_traffic_pattern"

    return {
        "road_id": int(
            latest["Junction"]
        ),

        "time": latest[
            "DateTime"
        ].isoformat(),

        "expected_vehicles": round(
            float(
                latest[
                    "predicted_vehicles"
                ]
            ),
            2
        ),

        "observed_vehicles": int(
            latest["Vehicles"]
        ),

        "expected_level":
            get_traffic_level(
                latest[
                    "predicted_vehicles"
                ]
            ),

        "observed_level":
            get_traffic_level(
                latest["Vehicles"]
            ),

        "residual": round(
            float(
                latest["residual"]
            ),
            2
        ),

        "anomaly_threshold": round(
            anomaly_threshold,
            2
        ),

        "flagged_as": flag,
    }


# =========================================================
# MAIN TEST
# =========================================================

if __name__ == "__main__":

    print(
        "TrafficVision M3 - "
        "Anomaly Detection"
    )

    print("=" * 55)

    print(
        "\nModel path:"
    )
    print(MODEL_PATH)

    print(
        "\nDataset path:"
    )
    print(DATA_PATH)

    print(
        "\nRunning anomaly detection..."
    )

    result = detect_anomalies(
        threshold_std=3.0,
        max_results=10
    )

    print(
        "\nAnomaly threshold:",
        result["threshold"]
    )

    print(
        "Total anomalies detected:",
        result["total_anomalies"]
    )

    print(
        "\nTop anomalies:"
    )

    if not result["anomalies"]:
        print(
            "No anomalies detected."
        )

    else:
        for anomaly in result[
            "anomalies"
        ]:
            print(
                anomaly
            )