# Setup Guide - Database & Redis Configuration

## Overview

This guide provides all team members with the necessary database and Redis connection details for local development, testing, and deployment.

---

## 1. Connection Strings

### PostgreSQL Database

```
postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision
```

**Connection Details:**

- **Host:** `postgres` (Docker) / `localhost` (Local)
- **Port:** `5432`
- **Database:** `trafficvision`
- **Username:** `traffic`
- **Password:** `change_me`
- **Driver:** `psycopg2` (PostgreSQL adapter for Python)

### Redis Cache

```
redis://redis:6379/0
```

**Connection Details:**

- **Host:** `redis` (Docker) / `localhost` (Local)
- **Port:** `6379`
- **Database:** `0` (default)
- **Protocol:** Redis protocol (no auth required in dev)

---

## 2. Environment Variables Setup

### For Development (`.env.dev`)

Create a `.env.dev` file in the project root with the following variables:

```bash
# PostgreSQL Configuration
POSTGRES_DB=trafficvision
POSTGRES_USER=traffic
POSTGRES_PASSWORD=change_me
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision

# Redis Configuration
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# Backend Configuration
BACKEND_PORT=8000
APP_ENV=development
PYTHONUNBUFFERED=1
```

### For Production (Environment-Specific)

Update the following variables based on your production environment:

```bash
DATABASE_URL=postgresql+psycopg2://traffic:YOUR_PROD_PASSWORD@prod-postgres-host:5432/trafficvision
REDIS_URL=redis://prod-redis-host:6379/0
```

---

## 3. Docker Compose Setup

### Development Environment

```bash
# Start all services (PostgreSQL, Redis, Backend)
docker compose -f docker-compose.dev.yml up --build

# Services will be available at:
# - Backend API: http://localhost:8000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Production Environment

```bash
# Start all services with production config
docker compose up --build

# Services will be available at:
# - Backend API: http://localhost:8000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

---

## 4. Service Health Checks

### PostgreSQL Health Check

```bash
# Via psql (if installed locally)
psql -h localhost -U traffic -d trafficvision -c "SELECT 1"

# Via Docker
docker compose exec postgres pg_isready -U traffic -d trafficvision
```

### Redis Health Check

```bash
# Via redis-cli (if installed locally)
redis-cli ping

# Via Docker
docker compose exec redis redis-cli ping
```

### Backend API Health Check

```bash
curl http://localhost:8000/health
```

---

## 5. Database Access

### Using Local Client

#### PostgreSQL

```bash
# Connect to PostgreSQL database
psql -h localhost -U traffic -d trafficvision -p 5432
# Password: change_me
```

#### Redis

```bash
# Connect to Redis
redis-cli -h localhost -p 6379
```

### Using Docker

#### PostgreSQL

```bash
docker compose exec postgres psql -U traffic -d trafficvision
# Password: change_me
```

#### Redis

```bash
docker compose exec redis redis-cli
```

---

## 6. Backend Configuration Reference

The backend application automatically reads connection strings from environment variables:

**File:** `backend/app/config.py`

```python
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://traffic:change_me@localhost:5432/trafficvision",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
```

---

## 7. Python Dependencies

Ensure the following packages are installed in the backend:

**File:** `backend/requirements.txt`

```
redis==5.0.8
psycopg2-binary  # PostgreSQL adapter
sqlalchemy       # ORM (if used)
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

---

## 8. Network Configuration

### Docker Network

All services in Docker Compose use the `trafficvision_net` network for inter-service communication.

**Service URLs within Docker Network:**

- PostgreSQL: `postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision`
- Redis: `redis://redis:6379/0`

### Local Development

Services are exposed on localhost with port mappings:

- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## 9. Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if service is running
docker compose ps postgres

# View logs
docker compose logs postgres

# Verify credentials
docker compose exec postgres psql -U traffic -d trafficvision -c "\l"
```

### Redis Connection Issues

```bash
# Check if service is running
docker compose ps redis

# View logs
docker compose logs redis

# Test connectivity
docker compose exec redis redis-cli ping
```

### Backend Connection Issues

```bash
# Check backend logs
docker compose logs backend

# Verify environment variables
docker compose exec backend env | grep -E "DATABASE_URL|REDIS_URL"

# Test connection from backend
docker compose exec backend python -c "from app.config import DATABASE_URL, REDIS_URL; print('DB:', DATABASE_URL); print('Redis:', REDIS_URL)"
```

---

## 10. Quick Start Checklist

- [ ] Copy `.env.dev.example` to `.env.dev`
- [ ] Update credentials if needed (change `change_me` for production)
- [ ] Run `docker compose -f docker-compose.dev.yml up --build`
- [ ] Verify PostgreSQL is running: `docker compose ps postgres`
- [ ] Verify Redis is running: `docker compose ps redis`
- [ ] Test API health: `curl http://localhost:8000/health`
- [ ] Verify database connection: `docker compose exec postgres psql -U traffic -d trafficvision -c "\dt"`
- [ ] Verify Redis connection: `docker compose exec redis redis-cli ping`

---

## 11. Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Python psycopg2 Documentation](https://www.psycopg.org/)
- [Python redis-py Documentation](https://github.com/redis/redis-py)

---

## Support

For issues or questions regarding database and Redis configuration:

1. Check the troubleshooting section above
2. Review Docker Compose logs: `docker compose logs -f`
3. Contact the DevOps team

---

**Last Updated:** 2026-08-29
**Version:** 1.0
