from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.rate_limit import check_rate_limit
from app.database.connection import Base, engine
from app.prediction.router import router as prediction_router
from app.route.router import router as route_router
from app.traffic.router import router as traffic_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for Traffic Prediction and "
        "Intelligent Congestion Management"
    ),
    version=settings.APP_VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(
    request: Request,
    call_next,
):
    if request.url.path not in [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]:
        client_id = request.client.host if request.client else "unknown"
        check_rate_limit(client_id)

    response = await call_next(request)
    return response


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    traffic_router,
    prefix="/api/v1",
)

app.include_router(
    prediction_router,
    prefix="/api/v1",
)

app.include_router(
    route_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "message": "TrafficVision AI Backend is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }