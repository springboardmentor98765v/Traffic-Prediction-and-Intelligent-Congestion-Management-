from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import Base, engine
from .routers import alerts

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Alert Service",
    description="Microservice for handling traffic alerts.",
    lifespan=lifespan
)

app.include_router(alerts.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "alert-service"}
