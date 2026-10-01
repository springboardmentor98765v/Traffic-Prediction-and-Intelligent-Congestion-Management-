import numpy as np
import pandas as pd

from src import prediction_model


class RecordingPipeline:
    def fit(self, features, labels):
        if not hasattr(self, "fit_rows"):
            self.fit_rows = []
        self.fit_rows.append(len(features))
        return self

    def predict(self, features):
        self.predicted_rows = len(features)
        return np.array(["LOW"] * len(features))


def test_training_fits_only_rows_before_chronological_cutoff(tmp_path, monkeypatch):
    rows = []
    for timestamp in pd.date_range("2026-01-01", periods=10, freq="D"):
        for road_id, level in (("1", "LOW"), ("2", "HIGH")):
            rows.append({
                "road_id": road_id,
                "timestamp": timestamp,
                "vehicle_count": 40,
                "average_speed": 45,
                "congestion_level": level,
            })
    data_path = tmp_path / "traffic.csv"
    pd.DataFrame(rows).to_csv(data_path, index=False)
    pipeline = RecordingPipeline()
    monkeypatch.setattr(prediction_model, "build_pipeline", lambda: pipeline)

    metrics = prediction_model.train_model(data_path, tmp_path / "model.joblib")

    assert pipeline.fit_rows == [16, 20]
    assert pipeline.predicted_rows == 4
    assert metrics["classes"] == ["HIGH", "LOW"]
    assert metrics["training_rows"] == 16
    assert metrics["test_rows"] == 4
    assert metrics["test_start"] == "2026-01-09T00:00:00"