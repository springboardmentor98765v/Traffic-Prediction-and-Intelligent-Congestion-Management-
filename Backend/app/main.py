from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.routers import auth, traffic, prediction, route
from app.database.connection import engine, Base
from app.middleware.rate_limit import RateLimitMiddleware
from app.services import ml_prediction_service

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description=(
        "Smart Traffic Prediction & Congestion Management System — Milestone 2\n\n"
        "## Authentication & Authorization\n"
        "Protected endpoints require a Bearer token in the `Authorization` header.\n"
        "Acquire tokens via `/api/v1/auth/login` or `/api/v1/auth/register`.\n\n"
        "## Role Hierarchy\n"
        "- **public**: Read-only access to live traffic, route optimization, and predictions.\n"
        "- **operator**: Access to monitoring, condition updates, aggregates, and reports.\n"
        "- **admin**: Full system access, user administration, and configuration.\n\n"
        "## Services & Capabilities\n"
        "- **Route Analysis**: Intelligent route optimization, alternate routes, travel-time, road conditions.\n"
        "- **AI Engine - Prediction**: Real trained model (`model-v1`), peak-hour forecasting, delay estimation, reports.\n"
        "- **Traffic Monitoring**: Live telemetry, historical time-series data, and rolled-up aggregations.\n"
        "- **Authentication**: Token generation, refresh flows, and RBAC enforcement."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
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
        "version": "2.0.0",
        "milestone": "Milestone 2 — Traffic Prediction & Route Optimization"
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "model_version": "model-v1",
        "services": {
            "auth": "online",
            "traffic_monitoring": "online",
            "ai_engine": "online",
            "route_analysis": "online"
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
