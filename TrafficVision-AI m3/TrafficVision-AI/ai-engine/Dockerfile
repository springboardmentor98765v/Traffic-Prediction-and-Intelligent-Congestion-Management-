FROM python:3.12-slim

WORKDIR /workspace/TrafficVision-AI/ai-engine

COPY ai-engine/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ai-engine /workspace/TrafficVision-AI/ai-engine

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
