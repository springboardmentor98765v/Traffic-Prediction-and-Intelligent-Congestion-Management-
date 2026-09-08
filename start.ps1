Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  TrafficVision AI — Milestone 1 Full Stack Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting FastAPI Backend Gateway on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python Backend/run.py"

Write-Host "Starting Next.js Web Frontend on http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Both services launched successfully in separate terminals!" -ForegroundColor Green
Write-Host "  - Backend API & Swagger: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Frontend Web UI:       http://localhost:3000" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
