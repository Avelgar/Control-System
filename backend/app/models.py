from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    login = Column(String(100), unique=True, index=True, nullable=False)
    fio = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    reg_token = Column(String(255), nullable=True)
    role = Column(String(50), default="observer", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())