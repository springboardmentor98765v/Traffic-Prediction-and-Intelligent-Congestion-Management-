from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, traffic, prediction
from app.database.connection import engine, Base

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Smart Traffic Prediction & Congestion Management System\n\n"
        "## Authentication\n"
        "All protected endpoints require a Bearer token in the Authorization header.\n"
        "Get a token via `/api/v1/auth/login`.\n\n"
        "## Roles\n"
        "- **admin**: Full access to all endpoints\n"
        "- **operator**: Access to traffic monitoring endpoints\n"
        "- **public**: Access to read-only traffic data\n\n"
        "## Services\n"
        "- **Authentication**: User registration, login, token management\n"
        "- **Traffic Monitoring**: Live traffic data, road status, density metrics\n"
        "- **AI Engine**: Congestion prediction (heuristic stub for Milestone 1)"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and token management operations.",
        },
        {
            "name": "Traffic Monitoring",
            "description": "Live traffic data, road status, and congestion metrics.",
        },
        {
            "name": "AI Engine - Prediction",
            "description": "Congestion prediction endpoints (heuristic stub for Milestone 1).",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
def root():
    return {"message": "Welcome to TrafficVision AI API", "version": settings.APP_VERSION}


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(traffic.router, prefix="/api/v1/traffic", tags=["Traffic Monitoring"])
app.include_router(prediction.router, prefix="/api/v1/predict", tags=["AI Engine - Prediction"])
