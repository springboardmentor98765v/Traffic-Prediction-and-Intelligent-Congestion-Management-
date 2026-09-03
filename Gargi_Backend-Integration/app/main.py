from app.database.connection import Base, engine
from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.traffic.router import router as traffic_router
from app.prediction.router import router as prediction_router
from app.core.config import settings

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for Traffic Prediction and"
        " Intelligent Congestion Management"
    ),
    version=settings.APP_VERSION,
)


app.include_router(auth_router, prefix="/api/v1")

app.include_router(traffic_router, prefix="/api/v1")

app.include_router(prediction_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "TrafficVision AI Backend is running", "status": "ok"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
