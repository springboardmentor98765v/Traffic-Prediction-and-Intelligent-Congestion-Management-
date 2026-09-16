from model import predict_congestion_ml


result, confidence = predict_congestion_ml(
    road_id_encoded=0,
    vehicle_count=20,
    avg_speed=30,
    density=40,
    hour=14,
    day_of_week=3
)

print("Prediction:", result)
print("Confidence:", confidence)