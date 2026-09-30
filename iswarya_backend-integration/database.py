from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Read individual database connection parameters from environment variables
# with intelligent defaults supporting both local development and Docker containers.
DB_USER = os.getenv("AUTH_DB_USER", "postgres")
DB_PASSWORD = os.getenv("AUTH_DB_PASSWORD", "12345678s")
DB_HOST = os.getenv("AUTH_DB_HOST", "postgres")
DB_PORT = os.getenv("AUTH_DB_PORT", "5432")
DB_NAME = os.getenv("AUTH_DB_NAME", "traffic_auth")

# Construct the SQLAlchemy connection URL dynamically
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()