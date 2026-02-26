"""
Database configuration dan session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base untuk models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency untuk mendapatkan database session
    
    Usage:
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inisialisasi database - ciptakan semua tables
    
    Note: Untuk production, gunakan Alembic migrations
    """
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created")


def close_db():
    """Close database connection"""
    engine.dispose()
    logger.info("✓ Database connection closed")

