import time
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from .config import settings
from .core.middleware import GatewayProductionMiddleware
from .auth import router as auth_router
from .gateway import traffic_proxy, prediction_proxy, route_proxy, alert_proxy, analytics_proxy
from .database import Base, engine, SessionLocal
from .models import User
from .auth.security import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Seed default accounts so they match docs.md and mainreadme.md
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(email="admin@trafficvision.ai").first():
            db.add(User(name="Admin", email="admin@trafficvision.ai", password_hash=get_password_hash("Admin@12345"), role="admin"))
            db.add(User(name="Operator", email="operator@trafficvision.ai", password_hash=get_password_hash("Operator@123"), role="traffic_operator"))
            db.add(User(name="Planner", email="planner@trafficvision.ai", password_hash=get_password_hash("Planner@123"), role="city_planner"))
            db.add(User(name="Commuter", email="commuter@trafficvision.ai", password_hash=get_password_hash("Commuter@123"), role="commuter"))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title="TrafficVision AI API Gateway",
    description="Main entry point for TrafficVision AI, handling auth, security, rate limiting, and routing to microservices.",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.middleware.gzip import GZipMiddleware

# 1. Automatic GZip response compression for payloads > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. Custom Gateway Production Middleware (Rate Limiting, Security Headers, Request ID, Logging)
app.add_middleware(GatewayProductionMiddleware)

# 2. Strict CORS Middleware: reads configured allow-list from environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Retry-After"]
)

# System Health & Readiness Probes
@app.get("/health", tags=["System"])
async def health_check():
    """Service liveness probe for container orchestrators and load balancers."""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/ready", tags=["System"])
async def readiness_check():
    """Service readiness probe verifying database connectivity."""
    db_status = "connected"
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "database": db_status}
        )

    return {
        "status": "ready",
        "service": "api-gateway",
        "database": db_status
    }


# Mount Subsystem Routers (Contracts strictly preserved)
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(traffic_proxy.router, prefix="/api/v1/traffic", tags=["traffic"])
app.include_router(prediction_proxy.router, prefix="/api/v1/predict", tags=["prediction"])
app.include_router(route_proxy.router, prefix="/api/v1/route", tags=["route"])
app.include_router(alert_proxy.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(analytics_proxy.router, prefix="/api/v1/analytics", tags=["analytics"])
