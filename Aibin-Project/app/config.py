"""
Configuration settings for the TrafficVision AI Gateway.
Reads settings from the environment or a .env file.
"""

import json
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application & Environment
    APP_NAME: str = "TrafficVision AI - Gateway & Auth Service"
    APP_ENV: str = "development"
    DEBUG: bool = False
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "info"

    # Database connection string
    DATABASE_URL: str = "sqlite:///./test.db"

    # Cache / Redis
    REDIS_URL: Optional[str] = "redis://127.0.0.1:6379/0"

    # JWT Strategy
    JWT_SECRET_KEY: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Microservices Upstream URLs
    DATA_ENGINEERING_URL: str = "http://127.0.0.1:8000"
    TRAFFIC_SERVICE_URL: str = "http://127.0.0.1:8000"
    AI_ENGINE_URL: str = "http://127.0.0.1:8001"
    PREDICTION_SERVICE_URL: str = "http://127.0.0.1:8001"
    ROUTE_ANALYSIS_URL: str = "http://127.0.0.1:8002"
    ALERT_SERVICE_URL: str = "http://127.0.0.1:8003"

    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"
    CORS_ORIGINS: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_GLOBAL_PER_MIN: int = 600
    RATE_LIMIT_AUTH_PER_MIN: int = 60

    # Proxy & Security
    TRUST_PROXIES: bool = True
    FORCE_HTTPS: bool = False
    MAX_REQUEST_BODY_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    REQUEST_TIMEOUT_SECONDS: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        """
        Parses CORS allowed origins from environment variables.
        Supports JSON arrays or comma-delimited strings.
        In production, wildcard '*' is strictly forbidden.
        """
        raw = self.CORS_ALLOWED_ORIGINS or self.CORS_ORIGINS or "http://localhost:3000"
        
        # Check if JSON array like ["http://localhost:3000"]
        if raw.strip().startswith("[") and raw.strip().endswith("]"):
            try:
                parsed = json.loads(raw)
                origins = [str(o).strip() for o in parsed if str(o).strip()]
            except Exception:
                origins = [raw.strip("[]").replace('"', "").replace("'", "").strip()]
        else:
            origins = [o.strip() for o in raw.split(",") if o.strip()]

        # Production security check: disallow wildcard in production
        if self.APP_ENV.lower() == "production" and "*" in origins:
            origins = [o for o in origins if o != "*"]
            if not origins:
                origins = ["http://localhost:3000"]

        return origins


settings = Settings()
