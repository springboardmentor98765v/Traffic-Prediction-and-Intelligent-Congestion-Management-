from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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
    description="Main entry point for TrafficVision AI, handling auth and routing to microservices.",
    lifespan=lifespan
)

# Add CORS Middleware so hariom-frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(traffic_proxy.router, prefix="/api/v1/traffic", tags=["traffic"])
app.include_router(prediction_proxy.router, prefix="/api/v1/predict", tags=["prediction"])
app.include_router(route_proxy.router, prefix="/api/v1/route", tags=["route"])
app.include_router(alert_proxy.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(analytics_proxy.router, prefix="/api/v1/analytics", tags=["analytics"])

