FROM python:3.10-slim

WORKDIR /app

# In a real setup we might copy a requirements.txt specifically for alert_service
# Here we'll just install fastapi, uvicorn, sqlalchemy, psycopg2
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv httpx

COPY . /app/alert_service

CMD ["uvicorn", "alert_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
