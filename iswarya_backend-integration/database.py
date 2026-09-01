from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("AUTH_DB_HOST", "localhost")
DB_PORT = os.getenv("AUTH_DB_PORT", "5432")
DB_NAME = os.getenv("AUTH_DB_NAME", "traffic_auth")
DB_USER = os.getenv("AUTH_DB_USER", "postgres")
DB_PASSWORD = os.getenv("AUTH_DB_PASSWORD", "postgres")

# Temporary direct connection to bypass .env loading issues
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/traffic_auth"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()