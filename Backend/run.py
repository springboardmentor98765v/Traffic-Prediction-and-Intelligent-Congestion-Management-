import sys
from pathlib import Path
import uvicorn

# Ensure the Backend directory is at the top of sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TrafficVision AI Backend Gateway Started")
    print("  -> Swagger UI (Interactive API Docs): http://127.0.0.1:8000/docs")
    print("  -> ReDoc UI:                         http://127.0.0.1:8000/redoc")
    print("  -> System Status:                    http://127.0.0.1:8000/health")
    print("=" * 60 + "\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(backend_dir))

