FROM python:3.12-slim

WORKDIR /service
COPY backend/services/ai-engine/ai-requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/services/ai-engine/app ./app
COPY aiml ./aiml
COPY data ./data

EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
