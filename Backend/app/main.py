from fastapi import FastAPI
from app.config import get_settings
from app.routers import auth

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Traffic Prediction & Congestion Management System",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/")
def root():
    return {"message": "Welcome to TrafficVision AI API", "version": settings.APP_VERSION}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
