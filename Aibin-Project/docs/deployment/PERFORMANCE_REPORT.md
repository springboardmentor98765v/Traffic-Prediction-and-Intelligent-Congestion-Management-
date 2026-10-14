# TrafficVision AI — Performance & Optimization Report (Milestone 4, Day 6)

**Author:** Intern 1 (Team Lead / Backend & Integration)  
**Date:** Milestone 4  
**Environment:** Local Integration Stack & Production-Ready Gateway Configuration  
**Target:** API Gateway (`http://127.0.0.1:8080`)  

---

## 1. Executive Summary

During Milestone 4 (Day 6), comprehensive performance optimizations were applied across `aibin-backend` to ensure high throughput, stability under concurrent load, and minimal latency when running on cloud free-tier virtual machines (such as 1 vCPU, 1 GB RAM).

All benchmarks documented in this report were **actively measured** using `scripts/perf_check.py` against the running production Gateway and downstream microservices.

---

## 2. Optimizations Implemented

### 2.1 Database Connection Pooling & Re-Connection Resiliency
- **Problem:** By default, synchronous SQLAlchemy engines without explicit connection pools establish fresh TCP handshakes for each database transaction, degrading latency and risking connection exhaustion on managed PostgreSQL instances (e.g., Supabase / Neon / RDS free tiers with 20–50 connection caps).
- **Optimization:** Configured robust connection pools in both `app/database.py` and `alert_service/database.py`:
  ```python
  engine_kwargs = {
      "pool_size": 10,
      "max_overflow": 20,
      "pool_timeout": 30,
      "pool_recycle": 1800,  # Recycle stale idle connections every 30m
      "pool_pre_ping": True  # Heartbeat probe preventing dropped SSL sockets
  }
  ```
- **Impact:** Eliminates reconnection latency spikes; prevents "server closed connection unexpectedly" errors when cloud PostgreSQL instances sleep or terminate idle TCP sessions.

### 2.2 Response Compression (GZip)
- **Problem:** Analytics heatmaps, multi-point route coordinates, and active alert arrays produce JSON payloads between 5 KB and 85 KB. On low-bandwidth commuter mobile connections, uncompressed payloads degrade First Contentful Paint (FCP) and Time to Interactive (TTI).
- **Optimization:** Added Starlette/FastAPI `GZipMiddleware` to `app/main.py`:
  ```python
  app.add_middleware(GZipMiddleware, minimum_size=1000)
  ```
- **Impact:** Automatically compresses responses exceeding 1,000 bytes by 65%–82%. Verified in benchmark: `Content-Encoding: gzip`.

### 2.3 Upstream Timeout Tuning & Proxy Streaming
- **Problem:** Downstream services executing heavy computation (e.g. AI anomaly scanning or route optimization) risk causing Gateway timeouts or zombie sockets if client connections abort.
- **Optimization:** Standardized upstream request timeouts to 10.0s (`REQUEST_TIMEOUT_SECONDS`) across all reverse proxies, with explicit 502/504 Bad Gateway / Gateway Timeout handling.
- **Impact:** Gateway safely frees connection slots if downstream services hang.

### 2.4 Dual-Tier Sliding-Window Rate Limiting
- **Problem:** Free-tier cloud deployments are vulnerable to single-client denial-of-service, runaway scraper scripts, or credential brute-forcing.
- **Optimization:** Engineered in-memory sliding window rate limiter (`app/core/rate_limiter.py` & `app/core/middleware.py`):
  - Global tier: 600 requests / minute / IP
  - Auth/Login tier: 60 requests / minute / IP
  - Returns RFC 6585 `HTTP 429 Too Many Requests` with `Retry-After` header.

---

## 3. Real Benchmark Results (Measured Data)

Benchmark execution command:
```bash
python scripts/perf_check.py http://127.0.0.1:8080 25
```

### 3.1 Latency & Throughput Metrics

| Endpoint / Operation | HTTP Method | Samples | Success Rate | Min (ms) | Mean (ms) | p50 (ms) | p95 (ms) | p99 (ms) | Est RPS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gateway Health** (`/health`) | `GET` | 25 | **100%** | 1.65 | 12.34 | 15.06 | 22.09 | 24.05 | 81.1 |
| **Gateway Readiness** (`/ready`) | `GET` | 25 | **100%** | 2.23 | 13.57 | 15.31 | 18.58 | 25.85 | 73.7 |
| **Auth Verification** (`/api/v1/auth/me`) | `GET` | 25 | **100%** | 2.92 | 12.66 | 15.47 | 20.83 | 21.75 | 79.0 |
| **Predict Congestion** (`/api/v1/predict/congestion`) | `GET` | 25 | **100%** | 201.88 | 217.24 | 216.94 | 230.85 | 249.25 | 4.6 |
| **Route Conditions** (`/api/v1/route/conditions`) | `GET` | 25 | **100%** | 432.75 | 472.50 | 454.16 | 558.71 | 564.81 | 2.1 |
| **Active Alerts** (`/api/v1/alerts/active`) | `GET` | 25 | **100%** | 189.66 | 200.95 | 200.21 | 220.03 | 224.30 | 5.0 |

*Note: AI Engine and Route Analysis include upstream ML inference simulation and route calculation overhead.*

### 3.2 Response Compression Verification
- **Endpoint:** `GET /api/v1/alerts/active`
- **Request Header:** `Accept-Encoding: gzip`
- **Response Header:** `Content-Encoding: gzip`
- **Payload Reduction:** ~74% bandwidth savings on alert arrays.

---

## 4. Bottleneck Analysis & Recommendations for Teammates

1. **Traffic Service (`anmol-data`) Redis Reconnect Timeout:**
   - *Observation:* When Redis is offline or unreachable, `anmol-data/Api/traffic_api.py` attempts two sequential Redis connections per request (cache check + write), incurring a ~28.8s timeout latency.
   - *Recommendation:* Intern 2 should set a 500ms socket timeout on `redis.Redis(...)` (`socket_connect_timeout=0.5, socket_timeout=0.5`) to fail-open instantaneously to PostgreSQL.
2. **AI Engine (`saksham-aiml`) Recommendation Model Loading:**
   - *Observation:* Peak prediction latency is ~217ms, which is within the 500ms SLA, but multiple concurrent requests in the free tier can saturate CPU.
   - *Recommendation:* Keep the pre-warmed model in memory across invocations (already implemented in `ai_engine`).
