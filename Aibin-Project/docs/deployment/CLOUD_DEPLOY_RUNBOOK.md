# TrafficVision AI — Cloud Deployment Runbook
**Target Platform:** Free-Tier Cloud VM (Ubuntu 22.04 / 24.04 LTS) + Docker Compose + Managed PostgreSQL  
**Author:** Intern 1 (Team Lead / Backend & Integration)  
**Milestone:** Milestone 4 (Testing, Deployment & Documentation)  
**Classification:** Standard Operating Procedure (SOP)  

---

## 1. Prerequisites & Account Setup

> [!IMPORTANT]
> The following steps require access to cloud console dashboards and credentials. Steps marked with **[MANUAL - needs human]** must be completed by the system owner or team members with account privileges.

* **[MANUAL - needs human]** Step 1.1: Provision a Free-Tier Cloud VM (e.g., Oracle Cloud Always Free 4-core Ampere / 24 GB RAM, AWS EC2 `t4g.small` / `t3.micro`, or Azure `B1s`).
  - OS: Ubuntu 22.04 LTS or 24.04 LTS x86_64 / arm64.
  - Security Group / Firewall Rules:
    - Port `22` (SSH): Allowed from your admin IP.
    - Port `8080` (API Gateway HTTP): Allowed from `0.0.0.0/0` (or `80`/`443` if using Nginx/Certbot).
* **[MANUAL - needs human]** Step 1.2: Provision a Managed PostgreSQL Database (Neon, Supabase, or Aiven Free Tier).
  - Copy the connection URI: `postgresql://user:password@host:5432/dbname?sslmode=require`.
* **[MANUAL - needs human]** Step 1.3: Run Database Schema Initialization.
  - Execute the SQL schema against the managed PostgreSQL database:
    ```bash
    psql "<YOUR_MANAGED_DATABASE_URL>" -f database/schema.sql
    ```

---

## 2. Server Environment Preparation

Connect to your remote Cloud VM via SSH:
```bash
ssh -i /path/to/key.pem ubuntu@<SERVER_PUBLIC_IP>
```

### Step 2.1: Install Docker & Docker Compose v2 on the VM
Run the automated Docker engine installation:
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release git

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow ubuntu user to execute docker without sudo
sudo usermod -aG docker $USER
newgrp docker
docker --version && docker compose version
```

### Step 2.2: Configure Swap Space (Vital for Free-Tier Memory Stability)
Prevent out-of-memory (OOM) killing during ML model loading:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 3. Cloning Repositories & Configuring Secrets

### Step 3.1: Clone the Project Repositories
Create a unified deployment root on the server:
```bash
mkdir -p ~/trafficvision && cd ~/trafficvision
git clone -b aibin-backend-and-Integration https://github.com/your-org/aibin-backend.git
git clone -b anmol-data-engineering https://github.com/your-org/anmol-data.git
git clone -b saksham-ai-ml https://github.com/your-org/saksham-aiml.git
git clone -b hariom-frontend-and-application-services https://github.com/your-org/hariom-frontend.git
```

### Step 3.2: Configure Production Environment Variables
* **[MANUAL - needs human]** Step 3.2.1: Generate a high-entropy secret key for JWT:
  ```bash
  openssl rand -hex 32
  ```
* **[MANUAL - needs human]** Step 3.2.2: Create and populate `.env.production` inside `~/trafficvision/aibin-backend`:
  ```bash
  cd ~/trafficvision/aibin-backend
  cp .env.production.example .env.production
  nano .env.production
  ```
  Fill in the exact values:
  ```env
  APP_ENV=production
  DATABASE_URL=postgresql://<DB_USER>:<DB_PASS>@<DB_HOST>:5432/<DB_NAME>?sslmode=require
  DB_HOST=<DB_HOST>
  DB_PORT=5432
  DB_NAME=<DB_NAME>
  DB_USER=<DB_USER>
  DB_PASSWORD=<DB_PASS>
  REDIS_URL=redis://redis:6379/0
  JWT_SECRET_KEY=<GENERATED_32_BYTE_HEX>
  CORS_ALLOWED_ORIGINS=http://localhost:3000,https://trafficvision.vercel.app
  RATE_LIMIT_GLOBAL_PER_MIN=120
  RATE_LIMIT_AUTH_PER_MIN=10
  TRUST_PROXIES=true
  FORCE_HTTPS=false
  ```

---

## 4. Stack Deployment & Verification

### Step 4.1: Launch Stack via Docker Compose
From `~/trafficvision/aibin-backend`:
```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

### Step 4.2: Inspect Container Status & Logs
Ensure all 6 containers are running and passing healthchecks:
```bash
docker compose -f docker-compose.prod.yml ps
```
Expected output:
```text
NAME                                IMAGE                                COMMAND                  STATUS
trafficvision-redis                 redis:7-alpine                       "redis-server --save…"   Up (healthy)
trafficvision-alert-service         trafficvision-alert-service:prod     "uvicorn alert_servi…"   Up (healthy)
trafficvision-route-analysis        trafficvision-route-analysis:prod    "uvicorn route_analy…"   Up (healthy)
trafficvision-traffic-monitoring    trafficvision-traffic-monitoring:prod "uvicorn Api.traffic…"   Up (healthy)
trafficvision-ai-engine             trafficvision-ai-engine:prod         "uvicorn ai_engine.m…"   Up (healthy)
trafficvision-gateway               trafficvision-gateway:prod           "uvicorn app.main:ap…"   Up (healthy)
```

### Step 4.3: Execute Smoke Test
Run the automated smoke test script against the Gateway:
```bash
chmod +x scripts/smoke-test.sh
./scripts/smoke-test.sh http://127.0.0.1:8080
```
Or remotely from your local workstation:
```bash
./scripts/smoke-test.sh http://<SERVER_PUBLIC_IP>:8080
```

---

## 5. Connecting Frontend to Cloud Gateway

* **[MANUAL - needs human]** Step 5.1: In Vercel / Cloud Dashboard for `hariom-frontend`:
  - Set Environment Variable:
    ```env
    NEXT_PUBLIC_API_URL=http://<SERVER_PUBLIC_IP>:8080/api/v1
    ```
    (Or `https://api.yourdomain.com/api/v1` if SSL domain is bound).
  - Trigger a redeployment in Vercel.
  - Verify that the web app successfully queries live traffic and displays map corridors.

---

## 6. Rollback Procedures

If a critical defect or service regression is discovered post-deployment:

### Scenario A: Fast Rollback to Previous Git Commit
```bash
cd ~/trafficvision/aibin-backend
git log -n 5 --oneline
# Checkout previous stable release
git checkout <PREVIOUS_COMMIT_SHA>
# Rebuild and restart services
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

### Scenario B: Restarting a Single Failing Service
If only a single service (e.g. `ai-engine`) crashes:
```bash
docker compose -f docker-compose.prod.yml restart ai-engine
docker compose -f docker-compose.prod.yml logs --tail=50 -f ai-engine
```

### Scenario C: Complete Emergency Teardown
```bash
docker compose -f docker-compose.prod.yml down
```
*(Note: External managed PostgreSQL data remains completely intact since database is managed externally).*
