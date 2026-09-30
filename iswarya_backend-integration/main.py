from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import your database engine and declarative base for table auto-creation
from app.database import engine
from app.models.user import Base  # Adjust path if your models base is located elsewhere
from app.models import alert      # <-- ADDED: Registers the Alert model for table creation

# Import your service routers (including Milestone 3 alerts)
from app.routes import auth, traffic, predict, route_analysis, alerts  # <-- ADDED: alerts

# ==========================================
# Lifespan Context Manager (Modern Startup/Shutdown)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically creates database tables on application startup 
    # if they do not already exist in PostgreSQL.
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic (if any) can go here

# ==========================================
# Initialize FastAPI Application First!
# ==========================================
app = FastAPI(
    title="Traffic Vision Backend API",
    description="""
    Production-ready backend API for real-time traffic monitoring, route analysis, and automated alerts.
    
    ## Features:
    * **Authentication & RBAC:** Secure token-based access with role scoping (`user`, `operator`, `admin`).
    * **Route Analysis & OSRM Fallback:** Robust routing capabilities with automatic 503 fallback handling if external map services fail.
    * **Automated Alerts:** Strict severity validation (`Low`, `Medium`, `High`, `Critical`) with timezone-aware UTC timestamps.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS Middleware to allow your frontend (Live Server / local ports) to communicate safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development and testing
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, PUT, DELETE)
    allow_headers=["*"],  # Allows all headers
)

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

# 1. Authentication Service Routes (Fixed prefix duplication)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# 2. Traffic Monitoring Service Routes (Live traffic, road density, utilization)
app.include_router(traffic.router, prefix="/api/v1/traffic", tags=["Traffic Monitoring"])

# 3. AI Engine Prediction Stub Route (Heuristic congestion prediction)
app.include_router(predict.router, prefix="/api/v1/predict", tags=["AI Prediction Stub"])

# 4. Route Analysis Service Routes (Milestone 2: Optimized paths, alternates, travel time)
app.include_router(route_analysis.router, prefix="/api/v1/route", tags=["Route Analysis"])

# 5. Alert Service Routes (Milestone 3: Automated congestion and anomaly alerts)
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])  # <-- ADDED