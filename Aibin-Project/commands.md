# TrafficVision AI — Quick Commands Reference (`commands.md`)

This document is a quick command cheat sheet for running, testing, and managing the `aibin-backend` API Gateway on **Windows (PowerShell)** and **Linux**.

---

## 📑 Quick Command Index

1. [Starting the Backend Gateway Server (Port 8080)](#1-starting-the-backend-gateway-server-port-8080)
2. [Activating the Virtual Environment](#2-activating-the-virtual-environment)
3. [Running Automated Pytest Tests](#3-running-automated-pytest-tests)
4. [Running Upstream Microservices](#4-running-upstream-microservices)
5. [Managing PostgreSQL Database Service](#5-managing-postgresql-database-service)
6. [Accessing Documentation & Web Dashboards](#6-accessing-documentation--web-dashboards)

---

## 🚀 1. Starting the Backend Gateway Server (Port 8080)

### On Windows (PowerShell):
```powershell
# Navigate to aibin-backend
cd "c:\Users\AIBIN SHIBU\OneDrive\Documents\trafficvision\aibin-backend"

# Start FastAPI Gateway on port 8080 with auto-reload
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8080 --reload
```

### On Linux / macOS:
```bash
cd /path/to/trafficvision/aibin-backend
source .venv/bin/activate
uvicorn app.main:app --port 8080 --reload
```

---

## 🐍 2. Activating the Virtual Environment

### Windows PowerShell:
```powershell
cd "c:\Users\AIBIN SHIBU\OneDrive\Documents\trafficvision\aibin-backend"
.\.venv\Scripts\Activate.ps1
```
*(If script execution is disabled, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Windows Command Prompt (cmd.exe):
```cmd
.\.venv\Scripts\activate.bat
```

### Linux / macOS (Bash / Zsh):
```bash
source .venv/bin/activate
```

---

## 🧪 3. Running Automated Pytest Tests

### Run Full Test Suite (Verbose):
```powershell
.\.venv\Scripts\pytest tests/ -v
```

### Run Only Authentication Tests:
```powershell
.\.venv\Scripts\pytest tests/test_auth.py -v
```

### Run Only Role-Based Access Control (RBAC) Tests:
```powershell
.\.venv\Scripts\pytest tests/test_rbac.py -v
```

### Run a Specific Test Function:
```powershell
.\.venv\Scripts\pytest tests/test_auth.py -k "test_login_success" -v
```

---

## 🌐 4. Running Upstream Microservices

Using the same `.venv` environment, you can run Anmol and Saksham's services in separate terminal tabs:

### Terminal 1: Run Anmol's Data Monitoring Service (Port 8000)
```powershell
cd "c:\Users\AIBIN SHIBU\OneDrive\Documents\trafficvision"
.\aibin-backend\.venv\Scripts\python.exe -m uvicorn anmol-data.Api.traffic_api:app --port 8000 --reload
```

### Terminal 2: Run Saksham's AI Engine Prediction Service (Port 8001)
```powershell
cd "c:\Users\AIBIN SHIBU\OneDrive\Documents\trafficvision\aibin-backend"
.\.venv\Scripts\python.exe -m uvicorn ai_engine.main:app --port 8001 --reload
```

### Terminal 3: Run Aibin's Backend API Gateway (Port 8080)
```powershell
cd "c:\Users\AIBIN SHIBU\OneDrive\Documents\trafficvision\aibin-backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8080 --reload
```

---

## 🗄️ 5. Managing PostgreSQL Database Service

### Check PostgreSQL Windows Service Status:
```powershell
Get-Service postgresql*
```

### Start PostgreSQL Windows Service:
```powershell
Start-Service postgresql*
```

### Stop PostgreSQL Windows Service:
```powershell
Stop-Service postgresql*
```

### Open PostgreSQL Interactive CLI (`psql`):
```powershell
psql -U postgres -d postgres -h 127.0.0.1 -p 5432
```
*(Password is **`A`**)*

### Initialize Auth/RBAC Database Schema:
```powershell
psql -U postgres -d postgres -h 127.0.0.1 -p 5432 -f "aibin-backend\database\schema.sql"
```

---

## 🌐 6. Accessing Documentation & Web Dashboards

| Service | URL |
|---|---|
| **Aibin Backend Swagger UI** | **[http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)** |
| **Aibin Backend Redoc UI** | [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc) |
| **Anmol Data Service Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| **Saksham AI Engine Docs** | [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) |
