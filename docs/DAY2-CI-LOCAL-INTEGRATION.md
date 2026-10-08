# Day 2 – CI & Local Integration

## 1. GitHub Actions CI Pipeline

The repository includes a GitHub Actions workflow that runs on pushes and pull requests to `main` and `develop`.

### Checks included

- Dependency installation for Python and Node
- JavaScript linting via ESLint
- Formatting checks via Prettier
- Python linting via Flake8
- Python formatting validation via Black
- Backend import and compile validation
- PostgreSQL and Redis service startup checks

### Pipeline file

- [.github/workflows/ci.yml](.github/workflows/ci.yml)

---

## 2. Docker Compose Development Environment

The local stack includes:

- PostgreSQL 16
- Redis 7
- FastAPI backend service

### Compose file

- [docker-compose.yml](docker-compose.yml)

### Run locally

```bash
docker compose up --build
```

Then validate the API with:

```bash
curl http://localhost:8000/health
```

---

## 3. Local Full-Stack Validation

The backend is prepared to validate services with the following environment variables:

- `DATABASE_URL`
- `REDIS_URL`

The startup checks ensure database and cache services can be reached during CI and local development.

---

## 4. Pull Request CI Readiness

This baseline is ready for branch protection and PR checks:

- Linting gate
- Formatting gate
- Python backend validation
- Service dependency startup validation
- Merge blocked until checks are green

---

## 5. Suggested Future Expansion

- Add frontend app service to the compose file
- Add a smoke test suite for API endpoints
- Add database migration scripts
- Add deployment workflow for staging and production
