# Milestone 4 — Production CI/CD Pipeline (lint → build → test → deploy)

Owner: Intern 5 · Date: 2026-10-04 · Requirement: FR-05, SRS §7.2

## Files

| File                                       | Purpose                                                                                            |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| `.github/workflows/ci.yml`                 | The pipeline (workflow name **CI/CD**). Adds `build` and `deploy` jobs to the M3 `tests`/lint jobs |
| `docker-compose.prod.yml`                  | Production stack the VM runs. Uses pre-built images only                                           |
| `.env.prod.example`                        | Production env var template, copied to the VM as `~/trafficvision/.env`                            |
| `QA/milestone4/day2/post_deploy_health.py` | Health gate run by the deploy job. A failure triggers rollback                                     |

## Stages

```
push / PR ──► lint ─────┐
          ├─► build ────┼──► deploy  (main only)
          └─► tests ────┘      ├─ upload docker-compose.prod.yml to VM
                               ├─ docker compose pull + up -d   (IMAGE_TAG=sha-<commit>)
                               ├─ post_deploy_health.py  (4 checks, 180 s)
                               └─ on health failure → redeploy previous_tag (rollback)
```

| Job      | Runs on                                                 | What it does                                                                                                                               |
| -------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `lint`   | every push/PR                                           | flake8 + Black (backend, analytics, QA), inline-JS syntax, ESLint, Prettier                                                                |
| `build`  | every push/PR                                           | Builds `backend`, `analytics`, `ai` images (matrix, GHA layer cache). **Pushes to GHCR only from `main`** as `:sha-<commit>` and `:latest` |
| `tests`  | every push/PR                                           | Postgres + Redis services, `pytest -q`, analytics suite, AI suite                                                                          |
| `deploy` | push to `main` or manual run on `main`; needs all three | SSH to the VM, pull the exact `sha-` images, restart, health-check, auto-rollback                                                          |

lint, build and tests run in parallel so developers get all failures at once. The SRS order
(lint → build → test → deploy) is enforced by deploy depending on all three.

Safety rules built in:

- PRs and `develop` never push images and never deploy.
- `concurrency: production-deploy` means one deploy at a time, and a running one is never cancelled.
- The `production` GitHub environment can require a manual approval (recommended after go-live).
- If the VM secrets aren't set yet, deploy ends with a warning ("not configured") instead of failing.
- The app's secrets are never in CI. They stay in the VM's `.env`.

## One-time setup (Day 3)

**1. VM** (Ubuntu 22.04/24.04, free tier, ≥1 GB RAM + 2 GB swap):

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER          # log out/in afterwards
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
mkdir -p ~/trafficvision && nano ~/trafficvision/.env   # contents from .env.prod.example
```

Open inbound ports 8000, 8001 and 8010 (plus 80/443 once TLS is added) in the cloud firewall.
Do **not** open 5432 or 6379.

**2. Deploy key**: run `ssh-keygen -t ed25519 -f deploy_key -N ""` and append `deploy_key.pub` to the
VM's `~/.ssh/authorized_keys`.

**3. GitHub → Settings → Environments → `production` → secrets:**

| Secret                               | Value                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------ |
| `DEPLOY_HOST`                        | VM public IP or DNS                                                                  |
| `DEPLOY_USER`                        | SSH user (e.g. `ubuntu`)                                                             |
| `DEPLOY_SSH_KEY`                     | contents of `deploy_key` (private)                                                   |
| `GHCR_PULL_USER` / `GHCR_PULL_TOKEN` | GitHub user + PAT with `read:packages`. Not needed if the 3 packages are made public |

**4.** Actions → CI/CD → **Run workflow** on `main`.

## Rollback

- Automatic: the deploy job writes `current_tag` / `previous_tag` on the VM. If the health gate fails,
  it restarts the stack on `previous_tag`.
- Manual: re-run the CI/CD workflow for an older commit, or on the VM run
  `IMAGE_PREFIX=ghcr.io/<owner>/trafficvision IMAGE_TAG=sha-<old> docker compose up -d`.
- Database: compose rollback does not undo schema/data changes. Intern 2's backup (Day 3) is the
  restore path.

## Known limits (tracked in `day1/defect_tracker.md`)

- Analytics is built from the backend Dockerfile with its own context, until Intern 1/2 ship a
  dedicated one.
- Lint is red repo-wide (DEF-M4-001), so deploy is blocked until owners clean their folders.
- No TLS yet. HTTPS is added with Intern 1's gateway config (Day 3).
- Frontend is hosted separately (Netlify/Vercel, Intern 4), not by this pipeline.
