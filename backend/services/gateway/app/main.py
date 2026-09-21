import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
TRAFFIC_SERVICE_URL = os.getenv("TRAFFIC_SERVICE_URL", "http://ai-engine:8003")
PREDICTION_SERVICE_URL = os.getenv("PREDICTION_SERVICE_URL", "http://ai-engine:8003")
ROUTE_ANALYSIS_SERVICE_URL = os.getenv("ROUTE_ANALYSIS_SERVICE_URL", "http://route-analysis:8004")
app = FastAPI(title="TrafficVision AI API Gateway", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}


async def forward(request: Request, base_url: str, path: str):
    target = f"{base_url}/{path}" if path else base_url
    headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host", "content-length"}}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            upstream = await client.request(request.method, target, params=request.query_params, content=await request.body(), headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Upstream service unavailable")
    return Response(content=upstream.content, status_code=upstream.status_code, headers={k: v for k, v in upstream.headers.items() if k.lower() not in {"content-length", "transfer-encoding", "connection"}}, media_type=upstream.headers.get("content-type"))


@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST"])
async def auth_gateway(path: str, request: Request):
    return await forward(request, AUTH_SERVICE_URL, f"api/v1/auth/{path}")


@app.api_route("/api/v1/traffic/{path:path}", methods=["GET"])
async def traffic_gateway(path: str, request: Request):
    return await forward(request, TRAFFIC_SERVICE_URL, f"api/v1/traffic/{path}")


@app.api_route("/api/v1/predict/{path:path}", methods=["GET"])
async def predict_gateway(path: str, request: Request):
    return await forward(request, PREDICTION_SERVICE_URL, f"api/v1/predict/{path}")


@app.api_route("/api/v1/route/rank", methods=["POST"])
async def route_rank_gateway(request: Request):
    return await forward(request, PREDICTION_SERVICE_URL, "api/v1/route/rank")


@app.api_route("/api/v1/route/{path:path}", methods=["GET", "POST"])
async def route_gateway(path: str, request: Request):
    return await forward(request, ROUTE_ANALYSIS_SERVICE_URL, f"api/v1/route/{path}")
