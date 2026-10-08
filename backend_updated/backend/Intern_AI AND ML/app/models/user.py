from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column("user_id", String, primary_key=True, index=True)
    username = Column(
        "username", String, unique=True, index=True, nullable=False
    )  # or name depending on your mapping
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)  # <--- Add this line
