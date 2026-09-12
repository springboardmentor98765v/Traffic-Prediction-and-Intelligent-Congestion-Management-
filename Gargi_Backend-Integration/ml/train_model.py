import os
import sys
import joblib
import pandas as pd

from sqlalchemy import text
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import engine


MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "congestion_model.joblib",
)


def load_data():
    query = text(
        """
        SELECT
            road_id,
            recorded_at,
            vehicle_count,
            density,
            congestion_level
        FROM traffic_records
        WHERE recorded_at IS NOT NULL
        ORDER BY recorded_at
        """
    )

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df


def prepare_data(df):
    df["recorded_at"] = pd.to_datetime(
        df["recorded_at"]
    )

    df["hour"] = df["recorded_at"].dt.hour
    df["day_of_week"] = df["recorded_at"].dt.dayofweek

    features = [
        "road_id",
        "hour",
        "day_of_week",
        "vehicle_count",
        "density",
    ]

    target = "congestion_level"

    X = df[features]
    y = df[target]

    return X, y


def train_model():
    print("Loading traffic data...")

    df = load_data()

    print(f"Records loaded: {len(df)}")

    if len(df) < 20:
        raise ValueError(
            "Not enough traffic records to train the model."
        )

    X, y = prepare_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("Training Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print(f"Model accuracy: {accuracy:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    os.makedirs(
        MODEL_DIR,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )


if __name__ == "__main__":
    train_model()