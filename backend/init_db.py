"""
Initialize database tables.
Run this once before seeding data.

Usage:
    python init_db.py
"""

import os
import sys
from sqlalchemy import create_engine

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/famcare")

engine = create_engine(DATABASE_URL, echo=True)

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("✓ Tables created successfully")
