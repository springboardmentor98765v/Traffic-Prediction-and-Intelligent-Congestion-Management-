"""
Database connection setup and dependency.
Uses SQLAlchemy to create an engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

# Connection pooling & resilience parameters
engine_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20
    engine_args["pool_timeout"] = 30
    engine_args["pool_recycle"] = 1800
    engine_args["pool_pre_ping"] = True

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
