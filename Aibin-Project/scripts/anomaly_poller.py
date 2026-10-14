# TEMP STOPGAP — remove once anmol-data/saksham-aiml implement real POST /api/v1/alerts calls — see dependencies.md DEP-01/DEP-03
import httpx
import asyncio
import time

AI_SERVICE_URL = "http://127.0.0.1:8001/api/v1/ai/anomalies"
ALERT_SERVICE_URL = "http://127.0.0.1:8003/api/v1/alerts"

async def poll_anomalies():
    print("Starting anomaly poller...")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Call Saksham's AI anomaly endpoint
                response = await client.get(AI_SERVICE_URL)
                
                # Check if stubbed or real
                if response.status_code == 200:
                    data = response.json()
                    # Example shape: { "road_id": "1", "flagged_as": "anomaly", "expected_level": "low", "observed_level": "high" }
                    # If data is a list of anomalies
                    if isinstance(data, list):
                        anomalies = data
                    else:
                        anomalies = [data] if data.get("flagged_as") else []
                        
                    for anomaly in anomalies:
                        if anomaly.get("flagged_as"):
                            print(f"Anomaly detected on road {anomaly.get('road_id')}. Creating accident alert.")
                            payload = {
                                "type": "accident",
                                "severity": "high",
                                "road_id": str(anomaly.get("road_id", "unknown")),
                                "message": f"AI flagged anomaly: Expected {anomaly.get('expected_level')}, observed {anomaly.get('observed_level')}."
                            }
                            await client.post(ALERT_SERVICE_URL, json=payload)
            except Exception as e:
                print(f"Poller error: {e}")
                
            # Short-interval polling
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(poll_anomalies())
