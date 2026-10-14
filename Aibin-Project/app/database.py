"""
Database connection setup and dependency.
Uses SQLAlchemy to create an engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

# For sqlite testing compatibility if needed, though we default to Postgres in .env
engine_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to provide a database session for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
