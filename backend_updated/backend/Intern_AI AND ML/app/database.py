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
    "DATABASE_URL", f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Providers (Neon, Render) hand out plain postgres:// / postgresql:// URLs. SQLAlchemy 2.1
# maps those to the psycopg (v3) driver, but this service ships psycopg2-binary, so pin the
# driver explicitly.
for _prefix in ("postgresql://", "postgres://"):
    if SQLALCHEMY_DATABASE_URL.startswith(_prefix):
        SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://" + SQLALCHEMY_DATABASE_URL[len(_prefix) :]
        break

# Managed Postgres (Neon) suspends idle compute and drops open connections, so check
# each pooled connection before use and recycle it before the provider's idle timeout.
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
