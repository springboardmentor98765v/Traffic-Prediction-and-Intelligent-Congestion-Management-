import os
import joblib
import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


# ============================================================
# PATHS
# ============================================================
#loaded the available traffic dataset from traffic.csv.
# The dataset contains 4k+ traffic records with traffic measurements, road information, timestamps and congestion labels.
DATA_PATH = "ai-engine/data/traffic.csv"
MODEL_PATH = "ai-engine/models/model-v1.joblib"


# ============================================================
# 1. LOAD DATA
# ============================================================

def load_data():

    print("Loading traffic dataset...")

    df = pd.read_csv(DATA_PATH)

    return df


# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

def create_features(df):
#converted the timestamp into usable time-based features — hour, day of week and weekend indicator. 
#These allow the model to learn differences in traffic patterns across different times and days.
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract time-based features
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    return df


# ============================================================
# 3. PREPARE DATA
# ============================================================

def prepare_data(df):
    # Features used for training.
    # They include traffic conditions and temporal information.
    features = [
        "vehicle_count",
        "avg_speed_kmph",
        "road_capacity",
        "road_length_km",
        "traffic_density_vehicles_per_km",
        "hour",
        "day_of_week",
        "is_weekend",
        "road_id",
    ]

    target = "congestion_level"

    X = df[features]
    y = df[target]

    return X, y
# ============================================================
# 4. BUILD RANDOM FOREST MODEL
# ============================================================

def build_model():

    numeric_features = [
        "vehicle_count",
        "avg_speed_kmph",
        "road_capacity",
        "road_length_km",
        "traffic_density_vehicles_per_km",
        "hour",
        "day_of_week",
        "is_weekend",
    ]

    categorical_features = [
        "road_id"
    ]

    # --------------------------------------------------------
    # Preprocessing
    # --------------------------------------------------------

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                "passthrough",
                numeric_features
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            ),
        ]
    )

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------
#used a Random Forest classifier with 300 trees.
#I also used balanced class weights because the congestion classes are not equally represented, especially the Severe class.
    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    # --------------------------------------------------------
    # Complete ML Pipeline
    # --------------------------------------------------------

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


# ============================================================
# 5. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

def time_based_split(df):

    print("\n===== TIME-BASED SPLIT =====")

    # Sort chronologically
    #Instead of randomly splitting the data, I used a chronological 80–20 split.
    df = df.sort_values("timestamp").reset_index(drop=True)

    split_index = int(len(df) * 0.80)

    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]

    print("Training samples:", len(train_df))
    print("Testing samples:", len(test_df))

    print("\nTraining period:")
    print(
        train_df["timestamp"].min(),
        "→",
        train_df["timestamp"].max()
    )

    print("\nTesting period:")
    print(
        test_df["timestamp"].min(),
        "→",
        test_df["timestamp"].max()
    )

    return train_df, test_df


# ============================================================
# 6. TRAIN MODEL
# ============================================================

def train():

    df = load_data()

    df = create_features(df)

    # --------------------------------------------------------
    # Chronological split
    # --------------------------------------------------------

    train_df, test_df = time_based_split(df)

    # --------------------------------------------------------
    # Prepare train/test data
    # --------------------------------------------------------

    X_train, y_train = prepare_data(train_df)
    X_test, y_test = prepare_data(test_df)

    # --------------------------------------------------------
    # Display features
    # --------------------------------------------------------

    print("\n===== FEATURES USED =====")

    for feature in X_train.columns:
        print("-", feature)

    # --------------------------------------------------------
    # Target distributions
    # --------------------------------------------------------

    print("\n===== TRAIN TARGET DISTRIBUTION =====")
    print(y_train.value_counts())

    print("\n===== TEST TARGET DISTRIBUTION =====")
    print(y_test.value_counts())

    # --------------------------------------------------------
    # Build model
    # --------------------------------------------------------

    pipeline = build_model()

    print("\nTraining Random Forest using chronological data...")
#After preprocessing the features, I trained the Random Forest model using the training portion of the dataset.
    pipeline.fit(
        X_train,
        y_train
    )

    print("Training completed successfully.")

    return pipeline, X_test, y_test


# ============================================================
# 7. EVALUATE MODEL
# ============================================================

def evaluate(model, X_test, y_test):

    print("\n===== TIME-BASED MODEL EVALUATION =====")

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    predictions = model.predict(X_test)

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------
#The model achieved 98.62% accuracy and 98.46% weighted F1 on the current time-based test set.
#evaluated the model using accuracy, weighted precision, weighted recall, F1 score, classification report and confusion matrix.
    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(f"\nAccuracy: {accuracy:.4f}")

    # --------------------------------------------------------
    # Precision
    # --------------------------------------------------------

    precision = precision_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print(f"Precision (weighted): {precision:.4f}")

    # --------------------------------------------------------
    # Recall
    # --------------------------------------------------------

    recall = recall_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print(f"Recall (weighted): {recall:.4f}")

    # --------------------------------------------------------
    # F1 Score
    # --------------------------------------------------------

    f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print(f"F1-score (weighted): {f1:.4f}")

    # --------------------------------------------------------
    # Classification Report
    # --------------------------------------------------------

    print("\n===== CLASSIFICATION REPORT =====")

    print(
        classification_report(
            y_test,
            predictions,
            labels=[
                "Low",
                "Medium",
                "High",
                "Severe"
            ],
            zero_division=0
        )
    )

    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    print("===== CONFUSION MATRIX =====")

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=[
            "Low",
            "Medium",
            "High",
            "Severe"
        ]
    )

    print("                 Predicted")
    print("              Low Medium High Severe")
    print("Actual Low   ", cm[0])
    print("Actual Medium", cm[1])
    print("Actual High  ", cm[2])
    print("Actual Severe", cm[3])

    return accuracy, precision, recall, f1


# ============================================================
# 8. SAVE MODEL
# ============================================================

def save_model(model):

    # Create models directory if needed
    os.makedirs(
        os.path.dirname(MODEL_PATH),
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print("\n===== MODEL SAVED =====")
    print("Model path:", MODEL_PATH)


# ============================================================
# 9. MAIN
# ============================================================

if __name__ == "__main__":

    model, X_test, y_test = train()

    accuracy, precision, recall, f1 = evaluate(
        model,
        X_test,
        y_test
    )

    # --------------------------------------------------------
    # Save only after successful training + evaluation
    # --------------------------------------------------------

    save_model(model)

    print("\n===== FINAL MODEL SUMMARY =====")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")

    print("\nM2 model training and validation completed successfully.")
