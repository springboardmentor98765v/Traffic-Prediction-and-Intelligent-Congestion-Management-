# Quick Reference - Database & Redis Connection Details

## 🚀 Quick Start

**Copy & Paste these connection strings:**

### PostgreSQL

```
postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision
```

### Redis

```
redis://redis:6379/0
```

---

## 📋 Credentials

| Service    | Host                 | Port | Username | Password  | Database      |
| ---------- | -------------------- | ---- | -------- | --------- | ------------- |
| PostgreSQL | postgres / localhost | 5432 | traffic  | change_me | trafficvision |
| Redis      | redis / localhost    | 6379 | N/A      | N/A       | 0             |

---

## 🐳 Docker Commands

```bash
# Start environment
docker compose -f docker-compose.dev.yml up --build

# Check services status
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down
```

---

## ✅ Health Checks

```bash
# PostgreSQL
docker compose exec postgres pg_isready -U traffic -d trafficvision

# Redis
docker compose exec redis redis-cli ping

# Backend API
curl http://localhost:8000/health
```

---

## 📝 Environment Variables

Create `.env.dev` in project root:

```bash
DATABASE_URL=postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision
REDIS_URL=redis://redis:6379/0
POSTGRES_DB=trafficvision
POSTGRES_USER=traffic
POSTGRES_PASSWORD=change_me
REDIS_PORT=6379
BACKEND_PORT=8000
```

---

## 🔗 Connection URLs

| Use Case                | URL                                                                    |
| ----------------------- | ---------------------------------------------------------------------- |
| Python Backend (Docker) | `postgresql+psycopg2://traffic:change_me@postgres:5432/trafficvision`  |
| Python Backend (Local)  | `postgresql+psycopg2://traffic:change_me@localhost:5432/trafficvision` |
| Redis (Docker)          | `redis://redis:6379/0`                                                 |
| Redis (Local)           | `redis://localhost:6379/0`                                             |

---

## 📞 Support

For detailed setup instructions, see: `docs/SETUP-GUIDE.md`

---

**⚠️ IMPORTANT:** Replace `change_me` with secure passwords for production environments!
