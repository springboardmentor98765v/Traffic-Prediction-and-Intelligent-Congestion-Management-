import httpx
import asyncio

# TEMP STOPGAP — remove once anmol-data/saksham-aiml implement real POST /api/v1/alerts calls — see dependencies.md DEP-01/DEP-03
# Polls route analysis / traffic delay to generate delay/closure alerts
ROUTE_SERVICE_URL = "http://127.0.0.1:8002/api/v1/route/travel-time"
ALERT_SERVICE_URL = "http://127.0.0.1:8003/api/v1/alerts"

async def check_delays_and_closures():
    print("Starting delay/closure trigger poller...")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Mock route_id for a standard route
                params = {"route_id": "rt_opt_129716_775946_to_129352_776245"}
                response = await client.get(ROUTE_SERVICE_URL, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    # If delay is excessively high, trigger a delay alert
                    # (Using > 20 for testing since mock delay is ~21.5m)
                    if data.get("congestion_delay_minutes", 0) > 20:
                        payload = {
                            "type": "delay",
                            "severity": "high",
                            "road_id": "route_1",
                            "message": f"Severe delay of {data.get('congestion_delay_minutes')} mins detected on optimal route."
                        }
                        await client.post(ALERT_SERVICE_URL, json=payload)
                        print(f"Triggered delay alert for {data.get('congestion_delay_minutes')} mins delay")
            except Exception as e:
                print(f"Trigger error: {e}")
                
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(check_delays_and_closures())
