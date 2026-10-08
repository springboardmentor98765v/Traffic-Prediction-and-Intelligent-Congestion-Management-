"""
TrafficVision AI — API Gateway (Day 5, minimal demo version)
Normally owned by: Intern 1 (Backend & Integration)
This version: built by Intern 2 to verify MY service integrates correctly
              through a Gateway, since Day 5 requires "confirmed working
              through the Gateway" as a checklist item.

Purpose:
    A single entry point that forwards requests to the Traffic Monitoring
    Service (main.py, running separately on port 8000). In the real
    project, Intern 1 owns this and also routes to Auth and Prediction
    services. This minimal version proves the ROUTING CONCEPT end-to-end
    so Day 5's checklist can be completed and demoed solo.

Requirements:
    pip install fastapi uvicorn httpx

Run (in a 3rd terminal, alongside ingest_live_data.py and main.py):
    uvicorn gateway:app --reload --port 9000

Then all traffic goes through the GATEWAY on port 9000, which forwards
to the real service on port 8000 — exactly like a production Gateway
would forward to internal microservices.
"""

import httpx
from fastapi import FastAPI, HTTPException, Request

app = FastAPI(
    title="TrafficVision AI — API Gateway (Day 5 demo)",
    description="Forwards /api/v1/traffic/* requests to the Traffic Monitoring Service",
    version="0.1.0",
)

# In the real system, Intern 1 would have a routing table like this
# mapping URL prefixes to internal service addresses.
SERVICE_ROUTES = {
    "traffic": "http://127.0.0.1:8000",   # Intern 2's Traffic Monitoring Service
    # "auth": "http://127.0.0.1:8001",    # Intern 1 would add Auth here
    # "predict": "http://127.0.0.1:8002", # Intern 1 would add Prediction stub here
}


@app.api_route("/api/v1/traffic/{path:path}", methods=["GET"])
async def gateway_forward(path: str, request: Request):
    """
    Catches ANY request starting with /api/v1/traffic/... and forwards
    it to the real Traffic Monitoring Service, then sends the response
    straight back — the Gateway itself doesn't know or care what's
    inside, it just routes.
    """
    target_base = SERVICE_ROUTES["traffic"]
    target_url = f"{target_base}/api/v1/traffic/{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, params=request.query_params, timeout=5.0)
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Traffic Monitoring Service is unreachable. Is main.py running on port 8000?",
            )

    return response.json()


@app.get("/")
def root():
    return {
        "service": "API Gateway (Day 5 demo)",
        "routes_registered": list(SERVICE_ROUTES.keys()),
        "note": "In the full project, Intern 1 owns this and also adds Auth + Prediction routing.",
    }
