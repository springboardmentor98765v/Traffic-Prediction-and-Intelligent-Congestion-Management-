from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

# Current project:
# Manasa-Maskan_AI-ML-Intelligent-Routing
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Parent folder:
# Traffic-Prediction-and-Intelligent-Congestion-Management-
PARENT_ROOT = PROJECT_ROOT.parent

# Sharmila's traffic dataset
DATA_PATH = (
    PARENT_ROOT
    / "Sharmila_Data-Engineering-Traffic-Monitoring"
    / "TrafficVision"
    / "data"
    / "traffic.csv"
)

# Trained model will be saved inside our src folder
MODEL_PATH = PROJECT_ROOT / "src" / "m2_traffic_model.pkl"


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 60)
print("M2 TRAFFIC PREDICTION MODEL TRAINING")
print("=" * 60)

print("\nDataset path:")
print(DATA_PATH)

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"\nTraffic dataset not found at:\n{DATA_PATH}"
    )

df = pd.read_csv(DATA_PATH)

print("\nDataset loaded successfully!")
print("Dataset shape:", df.shape)
print("Columns:", list(df.columns))


# ============================================================
# DATA PREPROCESSING
# ============================================================

df["DateTime"] = pd.to_datetime(df["DateTime"])

df["hour"] = df["DateTime"].dt.hour
df["day_of_week"] = df["DateTime"].dt.dayofweek
df["month"] = df["DateTime"].dt.month


# ============================================================
# FEATURES AND TARGET
# ============================================================

features = [
    "Junction",
    "hour",
    "day_of_week",
    "month",
]

X = df[features]
y = df["Vehicles"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# RANDOM FOREST MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
)

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)


# ============================================================
# MODEL EVALUATION
# ============================================================

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print("\n" + "=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(model, MODEL_PATH)

print("\n" + "=" * 60)
print("MODEL TRAINING COMPLETED")
print("=" * 60)

print("\nModel saved successfully:")
print(MODEL_PATH)

print("\nFeatures used:")
for feature in features:
    print("-", feature)

print("\nTarget:")
print("- Vehicles")

print("\n" + "=" * 60)