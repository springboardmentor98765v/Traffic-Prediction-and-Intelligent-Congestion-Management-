from src.ai_engine.anomaly_detector import detect_anomalies


print("=" * 60)
print("DAY 5 - ANOMALY DETECTION THRESHOLD TUNING")
print("=" * 60)

thresholds = [2.0, 2.5, 3.0, 3.5, 4.0]

print("\nTesting different anomaly thresholds...\n")

for threshold in thresholds:

    result = detect_anomalies(
        threshold_std=threshold,
        max_results=1000
    )

    total_anomalies = result.get(
        "total_anomalies",
        len(result.get("anomalies", []))
    )

    print(
        f"Threshold: {threshold:.1f} "
        f"-> Total anomalies: {total_anomalies}"
    )

print("\n" + "=" * 60)
print("Threshold tuning completed.")
print("=" * 60)