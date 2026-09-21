from src.congestion import calculate_congestion, predict_congestion


def test_low_congestion():
    assert calculate_congestion(45) == "LOW"


def test_medium_congestion():
    assert calculate_congestion(30) == "MEDIUM"


def test_high_congestion():
    assert calculate_congestion(15) == "HIGH"


def test_very_high_congestion():
    assert calculate_congestion(5) == "HIGH"


def test_prediction_uses_density_thresholds():
    assert predict_congestion(200, 45, 12)["predicted_level"] == "HIGH"
    assert predict_congestion(120, 45, 12)["predicted_level"] == "MEDIUM"
    assert predict_congestion(80, 45, 12)["predicted_level"] == "LOW"


def test_peak_hour_upgrades_low_prediction():
    result = predict_congestion(80, 45, 8)
    assert result["predicted_level"] == "MEDIUM"
    assert result["confidence"] == 0.75