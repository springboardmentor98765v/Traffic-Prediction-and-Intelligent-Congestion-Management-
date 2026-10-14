import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

DATA_PATH = "traffic_dataset_1000_combined.xlsx"
MODEL_SAVE_PATH = os.path.join("ai_engine", "traffic_model.joblib")


def load_and_preprocess_data(file_path: str):
    # 1. Read Excel spreadsheet into a pandas DataFrame
    df = pd.read_excel(file_path)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # 2. Extract time features if a timestamp exists
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["is_peak_hour"] = df["hour"].apply(
            lambda h: 1 if (8 <= h <= 11) or (17 <= h <= 20) else 0
        )
    else:
        df["hour"] = 12
        df["day_of_week"] = 2
        df["is_peak_hour"] = 0

    # 3. Select feature inputs
    feature_candidates = [
        "density",
        "vehicle_count",
        "avg_speed_kmph",
        "hour",
        "day_of_week",
        "is_peak_hour",
    ]
    features = [col for col in feature_candidates if col in df.columns]

    # 4. Identify or derive target label (LOW, MEDIUM, HIGH)
    target_col = None
    for cand in ["congestion_level", "congestion", "level"]:
        if cand in df.columns:
            target_col = cand
            break

    if not target_col:
        df["congestion_level"] = pd.cut(
            df["density"],
            bins=[-1, 0.40, 0.70, 1.0],
            labels=["LOW", "MEDIUM", "HIGH"],
        )
        target_col = "congestion_level"

    X = df[features]
    y = df[target_col].astype(str).str.upper()

    return X, y, features


def train():
    print(f"Loading data from {DATA_PATH}...")
    X, y, feature_names = load_and_preprocess_data(DATA_PATH)

    print(f"Features used: {feature_names}")
    print(f"Total samples: {len(X)}")

    # 5. Split data: 80% for training, 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 6. Initialize and fit Random Forest
    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)

    # 7. Evaluate on the test split
    y_pred = clf.predict(X_test)
    print("\n--- Model Evaluation ---")
    print(classification_report(y_test, y_pred))

    # 8. Export (serialize) model artifact to ai_engine/traffic_model.joblib
    model_payload = {
        "model": clf,
        "features": feature_names,
        "classes": clf.classes_.tolist(),
    }
    joblib.dump(model_payload, MODEL_SAVE_PATH)
    print(f"\nModel saved successfully to: {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    train()