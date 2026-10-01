from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
from src.prediction_model import train_model


if __name__ == "__main__":
    metrics = train_model(
        PROJECT_ROOT / "data" / "external" / "traffic_readings_export.csv",
        ROOT / "models" / "source_ml_v2.joblib",
    )
    print(metrics)
