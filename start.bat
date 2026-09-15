@echo off
echo ============================================================
echo   TrafficVision AI — Milestone 1 Full Stack Launcher
echo ============================================================
echo.
echo Starting FastAPI Backend Gateway on http://localhost:8000 ...
start "TrafficVision AI - Backend API (:8000)" cmd /k "python Backend/run.py"

echo Starting Next.js Web Frontend on http://localhost:3000 ...
start "TrafficVision AI - Frontend (:3000)" cmd /k "npm run dev"

echo.
echo ============================================================
echo   Both services are starting!
echo   - Backend Swagger Docs: http://localhost:8000/docs
echo   - Frontend Web Dashboard: http://localhost:3000
echo ============================================================
