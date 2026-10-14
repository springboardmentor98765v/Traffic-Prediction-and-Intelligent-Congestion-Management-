"""
Configuration settings for Route Analysis Microservice.
"""
from pydantic_settings import BaseSettings
from typing import Optional

class RouteSettings(BaseSettings):
    SERVICE_NAME: str = "Route Analysis Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8002
    
    # OpenStreetMap / OSRM Configuration (Free, Open-Source & Keyless)
    OSRM_BASE_URL: str = "https://router.project-osrm.org"
    OSRM_TIMEOUT_SECONDS: float = 3.5
    
    # Upstream AI Engine Prediction URL (Intern 3)
    AI_ENGINE_URL: str = "http://127.0.0.1:8001"
    
    # Upstream Data Engineering Service URL (Intern 2)
    DATA_ENGINEERING_URL: str = "http://127.0.0.1:8000"
    
    class Config:
        env_file = ".env"
        extra = "allow"

route_settings = RouteSettings()
