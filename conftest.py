import os
import sys
import tempfile
from pathlib import Path

# The backend's modules use absolute imports like `from app.database import engine`,
# which assumes the backend folder itself is on sys.path — matching how the Docker
# image runs it (WORKDIR /app, `uvicorn app.main:app`). Add it here so tests can do
# `from app.main import app`. BACKEND_DIR overrides the location (same variable as
# docker-compose.dev.yml).
BACKEND_DIR = Path(__file__).resolve().parent / os.getenv(
    "BACKEND_DIR", "backend_updated/backend/Intern_AI AND ML"
)
sys.path.insert(0, str(BACKEND_DIR))

ANALYTICS_DIR = Path(__file__).resolve().parent / os.getenv(
    "ANALYTICS_DIR", "daa/M3_Day6_Traffic_Monitoring_"
)
sys.path.insert(0, str(ANALYTICS_DIR / "src"))

os.environ.setdefault("JWT_SECRET_KEY", "test-only-milestone3-jwt-secret-2026")
os.environ.setdefault("ALERT_SERVICE_KEY", "test-only-milestone3-alert-key")

# In-process API tests (TestClient) need a database. Without DATABASE_URL the backend
# defaults to the Compose-only host `postgres`, which fails outside Docker
# (DEF-M3-002). Default to a throwaway SQLite file; CI and Docker set DATABASE_URL
# explicitly, and load_dotenv() in app/database.py never overrides it.
os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///" + (Path(tempfile.mkdtemp(prefix="tv-tests-")) / "test.db").as_posix(),
)
