# ==============================================================================
# TrafficVision AI — Route Analysis Microservice (Production Dockerfile)
# Owner: Intern 1 (Team Lead / Backend & Integration)
# ==============================================================================

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

COPY route_analysis/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production runtime image
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PATH=/home/appuser/.local/bin:$PATH

RUN groupadd -g 10001 appuser \
    && useradd -u 10001 -g appuser -s /bin/bash -m appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser route_analysis /app/route_analysis

USER appuser

EXPOSE 8002

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')" || exit 1

CMD ["uvicorn", "route_analysis.main:app", "--host", "0.0.0.0", "--port", "8002"]
