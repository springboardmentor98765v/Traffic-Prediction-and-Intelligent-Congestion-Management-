from model import predict_congestion_ml


def test_ml_prediction():
    result, confidence = predict_congestion_ml(
        road_id_encoded=0,
        vehicle_count=20,
        avg_speed=30,
        density=40,
        hour=14,
        day_of_week=3
    )

    assert result in ["Low", "Medium", "High", "LOW", "MEDIUM", "HIGH"]
    assert confidence is not None
    assert 0 <= confidence <= 1

    print("ML prediction test passed!")
    print("Prediction:", result)
    print("Confidence:", confidence)


def test_peak_hour_input():
    result, confidence = predict_congestion_ml(
        road_id_encoded=0,
        vehicle_count=40,
        avg_speed=20,
        density=70,
        hour=18,
        day_of_week=3
    )

    assert result in ["Low", "Medium", "High", "LOW", "MEDIUM", "HIGH"]

    print("Peak-hour prediction test passed!")


if __name__ == "__main__":
    test_ml_prediction()
    test_peak_hour_input()

    print("All ML service tests passed!")