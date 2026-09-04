from congestion_predictor import predict_congestion


test_cases = [
    (10, 14),
    (30, 14),
    (60, 14),
    (10, 8),
    (30, 18),
    (60, 12)
]


for density, hour in test_cases:
    result = predict_congestion(density, hour)

    print(
        f"Density: {density}, "
        f"Hour: {hour}, "
        f"Prediction: {result}"
    )