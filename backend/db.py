import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://costadmin:costpass123@localhost:5432/costdetective")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    region = Column(String, nullable=False)
    resources_scanned = Column(Integer, default=0)
    issues_found = Column(Integer, default=0)
    estimated_savings = Column(Float, default=0.0)
    analysis_result = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="analyses")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
