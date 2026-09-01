from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your database engine and declarative base for table auto-creation
from app.database import engine
from app.models.user import Base  # Adjust path if your models base is located elsewhere

# Import your service routers
from app.routes import auth, traffic, predict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI Application (Serving as the Central API Gateway)
app = FastAPI(
    title="TrafficVision AI API",
    version="1.0.0",
    description="Central API Gateway for TrafficVision AI - Milestone 1"
)

# Add CORS Middleware to allow Swagger UI and frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Configure CORS Middleware to allow your frontend (Live Server / local ports) to communicate safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development and testing
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, PUT, DELETE)
    allow_headers=["*"],  # Allows all headers
)

# ==========================================
# Database Startup Event Initialization
# ==========================================
@app.on_event("startup")
def on_startup():
    """
    Automatically creates database tables on application startup 
    if they do not already exist in PostgreSQL.
    """
    Base.metadata.create_all(bind=engine)


# ==========================================
# System Health Check Endpoint
# ==========================================
@app.get("/health", tags=["System Health"])
def health_check():
    """
    Health check endpoint to verify the backend server is alive and reachable.
    """
    return {"status": "ok"}


# ==========================================
# API Gateway Route Registrations
# ==========================================

# 1. Authentication Service Routes (Register, Login, Refresh, Me & RBAC roles)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# 2. Traffic Monitoring Service Routes (Live traffic, road density, utilization)
app.include_router(traffic.router, prefix="/api/v1/traffic", tags=["Traffic Monitoring"])

# 3. AI Engine Prediction Stub Route (Heuristic congestion prediction)
app.include_router(predict.router, prefix="/api/v1/predict", tags=["AI Prediction Stub"])