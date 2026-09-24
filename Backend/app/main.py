from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.routers import auth, traffic, prediction, route, alerts, analytics, ai
from app.database.connection import engine, Base
from app.middleware.rate_limit import RateLimitMiddleware
from app.services import ml_prediction_service

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="3.0.0",
    description=(
        "Smart Traffic Prediction & Congestion Management System — Milestone 3\n\n"
        "## Authentication & Authorization\n"
        "Protected endpoints require a Bearer token in the `Authorization` header.\n"
        "Acquire tokens via `/api/v1/auth/login` or `/api/v1/auth/register`.\n\n"
        "## Role Hierarchy\n"
        "- **public**: Read-only access to live traffic, route optimization, predictions, and public-safety alerts.\n"
        "- **operator**: Access to monitoring, road condition updates, alert creation/management, aggregates, and analytics reports.\n"
        "- **admin**: Full system access, all active/historical alerts, user administration, and system configuration.\n\n"
        "## Services & Capabilities\n"
        "- **Alert Service**: In-app notifications for congestion, accidents, closures, and delays with role-scoping and real-time delivery.\n"
        "- **Analytics Service**: Multi-timeframe trend analysis, 2D congestion heatmaps, and downloadable historical reports.\n"
        "- **AI Engine - Insights**: Anomaly detection for incident flagging and explainable AI traffic recommendations.\n"
        "- **Route Analysis**: Intelligent route optimization, alternate routes, travel-time, road conditions.\n"
        "- **AI Engine - Prediction**: Trained ML model (`model-v1`), peak-hour forecasting, delay estimation, reports.\n"
        "- **Traffic Monitoring**: Live telemetry, historical time-series data, and rolled-up aggregations.\n"
        "- **Authentication**: Token generation, refresh flows, and RBAC enforcement."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Alert Service & Notifications",
            "description": "Traffic alerts (congestion, accidents, closures, delays), in-app notifications, and real-time delivery.",
        },
        {
            "name": "Analytics Service",
            "description": "Traffic trend patterns, 2D congestion heatmap matrices, and downloadable historical reports.",
        },
        {
            "name": "AI Engine - Insights & Recommendations",
            "description": "Traffic anomaly detection, accident auto-triggers, and AI-powered route/departure recommendations.",
        },
        {
            "name": "Route Analysis",
            "description": "Route optimization, congestion-aware alternate routes, travel-time estimation, and road conditions.",
        },
        {
            "name": "AI Engine - Prediction",
            "description": "Trained ML model (model-v1) congestion forecasting, peak hours, delay estimation, and reports.",
        },
        {
            "name": "Traffic Monitoring",
            "description": "Live traffic conditions, historical readings, aggregations, and road-condition tracking.",
        },
        {
            "name": "Authentication",
            "description": "User registration, login, and token management operations.",
        },
        {
            "name": "System",
            "description": "Health check and system status operations.",
        },
    ],
)

# Middleware: Rate limiting & CORS
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Prime the trained ML model on service startup."""
    try:
        ml_prediction_service.get_trained_model()
    except Exception:
        pass


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to TrafficVision AI API",
        "version": "3.0.0",
        "milestone": "Milestone 3 — Alerts, Analytics & AI Insights"
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "model_version": "model-v1",
        "services": {
            "auth": "online",
            "traffic_monitoring": "online",
            "ai_engine": "online",
            "route_analysis": "online",
            "alert_service": "online",
            "analytics_service": "online",
            "ai_insights": "online"
        }
    }


@app.get("/pages", include_in_schema=False)
def pages_redirect():
    return RedirectResponse(url="/docs")


# Register API Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(traffic.router, prefix="/api/v1/traffic", tags=["Traffic Monitoring"])
app.include_router(prediction.router, prefix="/api/v1/predict", tags=["AI Engine - Prediction"])
app.include_router(route.router, prefix="/api/v1/route", tags=["Route Analysis"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alert Service & Notifications"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics Service"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Engine - Insights & Recommendations"])
