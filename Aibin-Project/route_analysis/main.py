"""
Route Analysis Microservice Entry Point.
TrafficVision AI — Milestone 2 (Owner: Intern 1 / Backend & Integration)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import route_settings
from .router import router as route_router
from .schemas import HealthResponse

app = FastAPI(
    title="TrafficVision AI — Route Analysis Service",
    description="Microservice for OpenStreetMap corridor path resolution, route optimization, and alternate route generation.",
    version=route_settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Service liveness and health check endpoint."""
    return HealthResponse(
        status="healthy",
        service=route_settings.SERVICE_NAME,
        version=route_settings.SERVICE_VERSION,
        maps_provider="OpenStreetMap / OSRM"
    )

@app.get("/", tags=["Root"])
async def root():
    """Root metadata endpoint."""
    return {
        "service": route_settings.SERVICE_NAME,
        "status": "online",
        "version": route_settings.SERVICE_VERSION,
        "docs": "/docs"
    }

# Mount route analysis endpoints
app.include_router(route_router, prefix="/api/v1/route", tags=["Route Analysis"])
