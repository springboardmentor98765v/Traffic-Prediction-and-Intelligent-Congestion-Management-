# TEMP STOPGAP — remove once anmol-data/saksham-aiml implement real POST /api/v1/alerts calls — see dependencies.md DEP-01/DEP-03
import httpx
import asyncio

async def simulate_trigger():
    # Calling the internal Alert Service endpoint directly on 8003
    payload = {
        "type": "congestion",
        "severity": "high",
        "road_id": "1",
        "message": "Congestion threshold breached on road 1"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8003/api/v1/alerts", json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed to reach Alert Service: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_trigger())
