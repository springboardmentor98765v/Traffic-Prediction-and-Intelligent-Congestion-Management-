import time
from model import predict_congestion_ml

start = time.perf_counter()

for _ in range(100):
    predict_congestion_ml(
        road_id_encoded=0,
        vehicle_count=20,
        avg_speed=30,
        density=40,
        hour=14,
        day_of_week=3
    )

end = time.perf_counter()

total_time = end - start
average_time = total_time / 100

print("Total time for 100 predictions:", round(total_time, 4), "seconds")
print("Average prediction time:", round(average_time * 1000, 4), "ms")

assert average_time < 2

print("Latency test passed!")