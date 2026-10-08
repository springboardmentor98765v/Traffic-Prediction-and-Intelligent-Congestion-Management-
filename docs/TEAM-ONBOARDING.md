# Team Onboarding - Database & Redis Setup

## 👋 Welcome to TrafficVision!

This guide provides all the information you need to connect to our databases and caching layer.

---

## 📌 Connection Details Summary

### PostgreSQL Database

| Property          | Value           |
| ----------------- | --------------- |
| **Host (Docker)** | `postgres`      |
| **Host (Local)**  | `localhost`     |
| **Port**          | `5432`          |
| **Username**      | `traffic`       |
| **Password**      | `change_me`     |
| **Database Name** | `trafficvision` |
| **Driver**        | `psycopg2`      |

**Connection String:**

```
postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision
```

---

### Redis Cache

| Property           | Value              |
| ------------------ | ------------------ |
| **Host (Docker)**  | `redis`            |
| **Host (Local)**   | `localhost`        |
| **Port**           | `6379`             |
| **Database Index** | `0`                |
| **Auth**           | Not required (dev) |

**Connection String:**

```
redis://redis:6379/0
```

---

## 🔧 Setup Instructions

### Step 1: Clone and Navigate

```bash
git clone <repository-url>
cd Traffic-Prediction-and-Intelligent-Congestion-Management-
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.dev.example .env.dev

# The .env.dev file will contain:
DATABASE_URL=postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision
REDIS_URL=redis://redis:6379/0
```

### Step 3: Start Services

```bash
# Start Docker Compose with development configuration
docker compose -f docker-compose.dev.yml up --build

# Services will be available at:
# - Backend: http://localhost:8000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Step 4: Verify Connections

```bash
# Check all services are running
docker compose ps

# Test PostgreSQL
docker compose exec postgres psql -U traffic -d trafficvision -c "\dt"

# Test Redis
docker compose exec redis redis-cli ping

# Test Backend API
curl http://localhost:8000/health
```

---

## 💻 Connecting to Databases

### Using Python (Backend)

```python
import os
from sqlalchemy import create_engine
from redis import Redis

# PostgreSQL connection
db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://traffic:change_me@localhost:5432/trafficvision")
engine = create_engine(db_url)

# Redis connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(redis_url)
```

### Using Command Line

#### PostgreSQL

```bash
# Via Docker Compose
docker compose exec postgres psql -U traffic -d trafficvision

# Via local psql (if installed)
psql -h localhost -U traffic -d trafficvision -p 5432
# When prompted for password, enter: change_me
```

#### Redis

```bash
# Via Docker Compose
docker compose exec redis redis-cli

# Via local redis-cli (if installed)
redis-cli -h localhost -p 6379
```

### Using GUI Tools

#### PostgreSQL (pgAdmin / DBeaver)

- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `trafficvision`
- **Username:** `traffic`
- **Password:** `change_me`

#### Redis (Redis Desktop Manager / Another Redis Desktop Manager)

- **Host:** `localhost`
- **Port:** `6379`
- **Name:** `Local Redis`

---

## 🔗 Environment Variables Reference

| Variable            | Value                                                                 | Used By              |
| ------------------- | --------------------------------------------------------------------- | -------------------- |
| `DATABASE_URL`      | `postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision` | Backend API          |
| `REDIS_URL`         | `redis://redis:6379/0`                                                | Backend API, Caching |
| `POSTGRES_DB`       | `trafficvision`                                                       | PostgreSQL Service   |
| `POSTGRES_USER`     | `traffic`                                                             | PostgreSQL Service   |
| `POSTGRES_PASSWORD` | `change_me`                                                           | PostgreSQL Service   |
| `POSTGRES_PORT`     | `5432`                                                                | Docker Port Mapping  |
| `REDIS_PORT`        | `6379`                                                                | Docker Port Mapping  |
| `BACKEND_PORT`      | `8000`                                                                | Docker Port Mapping  |

---

## 📚 Documentation Links

| Document                                                     | Purpose                                       |
| ------------------------------------------------------------ | --------------------------------------------- |
| [SETUP-GUIDE.md](SETUP-GUIDE.md)                             | Comprehensive setup and troubleshooting guide |
| [QUICK-REFERENCE.md](QUICK-REFERENCE.md)                     | Quick commands and connection strings         |
| [DAY2-CI-LOCAL-INTEGRATION.md](DAY2-CI-LOCAL-INTEGRATION.md) | CI/CD and Docker Compose details              |

---

## ⚠️ Important Notes

### Security

- **Development:** The password `change_me` is for development only
- **Production:** Always use strong, unique passwords for production environments
- **Credentials:** Never commit `.env.dev` to version control (it's in `.gitignore`)

### Network Access

- **Docker Network:** Services communicate via `trafficvision_net`
- **Local Development:** Services are exposed on `localhost` with port forwarding
- **Production:** Update hosts and ports according to your infrastructure

### Troubleshooting

If you encounter connection issues:

```bash
# 1. Check if services are running
docker compose ps

# 2. View service logs
docker compose logs postgres
docker compose logs redis
docker compose logs backend

# 3. Verify environment variables
docker compose exec backend env | grep -E "DATABASE_URL|REDIS_URL"

# 4. Test connectivity directly
docker compose exec backend python -c "import psycopg2; print('PostgreSQL OK')"
docker compose exec backend python -c "import redis; print('Redis OK')"
```

---

## 🚀 Next Steps

1. **Set up your IDE:** Configure your editor with Python extensions
2. **Install dependencies:** `pip install -r backend/requirements.txt`
3. **Create feature branch:** Start working on your assigned tasks
4. **Review PR checklist:** [docs/PR-REVIEW-CHECKLIST.md](../docs/PR-REVIEW-CHECKLIST.md)

---

## 📞 Need Help?

- Check the [SETUP-GUIDE.md](SETUP-GUIDE.md) for detailed troubleshooting
- Review Docker Compose logs: `docker compose logs -f`
- Contact your team lead or DevOps engineer

---

**Last Updated:** 2026-08-29
**Version:** 1.0
