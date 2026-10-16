import requests
from anomaly_detector import AnomalyDetector  # Assuming Intern 3's detector file is available

# Your backend Alert API endpoint
ALERT_API_URL = "http://127.0.0.1:8000/api/v1/alerts/"

def process_and_trigger_alerts():
    detector = AnomalyDetector()
    
    # Example live observation simulation (or batch data check)
    # Using sample data format expected by AnomalyDetector.analyze()
    sample_observation = {
        "road_id": "R001",
        "timestamp": "2026-09-23T08:00:00",
        "vehicle_count": 85,
        "avg_speed_kmph": 15.0,
        "traffic_density": 25.0
    }
    
    # Run analysis using Intern 3's detector logic
    result = detector.analyze(
        road_id=sample_observation["road_id"],
        timestamp=sample_observation["timestamp"],
        vehicle_count=sample_observation["vehicle_count"],
        avg_speed_kmph=sample_observation["avg_speed_kmph"],
        traffic_density=sample_observation["traffic_density"]
    )
    
    print("Anomaly Analysis Result:", result)
    
    # Check if it's classified as a possible_incident
    if result.get("anomaly_class") == "possible_incident":
        payload = {
            "type": "accident",
            "severity": "High",
            "road_id": result["road_id"],
            "message": f"AI anomaly detector flagged a possible_incident on road {result['road_id']}."
        }
        
        # Send POST request to your backend Alert Service
        try:
            response = requests.post(ALERT_API_URL, json=payload)
            if response.status_code == 201:
                print("Successfully triggered automated accident alert:", response.json())
            else:
                print("Failed to trigger alert:", response.text)
        except Exception as e:
            print("Connection error to Alert Service:", e)

if __name__ == "__main__":
    process_and_trigger_alerts()