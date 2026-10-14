"""
Configuration settings for the TrafficVision AI Gateway.
Reads settings from the environment or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Database connection string
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # JWT Strategy:
    # We use symmetric encryption (HS256) with a secret key.
    # Access tokens are short-lived, while refresh tokens are longer-lived.
    # The JWT_SECRET_KEY must be changed in production.
    JWT_SECRET_KEY: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External service URLs
    DATA_ENGINEERING_URL: str = "http://127.0.0.1:8000"
    AI_ENGINE_URL: str = "http://127.0.0.1:8001"
    ROUTE_ANALYSIS_URL: str = "http://127.0.0.1:8002"
    TRAFFIC_SERVICE_URL: str = "http://127.0.0.1:8000"
    PREDICTION_SERVICE_URL: str = "http://127.0.0.1:8001"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
