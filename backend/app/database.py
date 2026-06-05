import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Load backend/.env explicitly so uvicorn, pytest, and direct module imports
# all see the same database settings.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/famcare")

# Use NullPool for testing to avoid connection persistence issues
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    poolclass=NullPool if "pytest" in os.environ.get("RUNNING_TESTS", "") else None,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency injection for FastAPI - get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
