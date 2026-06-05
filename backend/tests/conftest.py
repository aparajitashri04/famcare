"""
pytest fixtures and configuration for test database.
Each test runs in isolation with its own transaction.
"""

import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models import Base, Service, Caregiver, Patient
from app.database import get_db
from app.main import app

# Use in-memory SQLite for fast tests
# Alternatively, use PostgreSQL test database if you prefer
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///:memory:",
)


@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database and session.
    Automatically rolls back after each test.
    """
    
    # Create engine
    if "sqlite" in TEST_DATABASE_URL:
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(TEST_DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI test client with test database dependency.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture(scope="function")
def seed_data(test_db: Session):
    """
    Seed test database with services, caregivers, and patient.
    Also creates service-caregiver relationships.
    """
    # Services
    services = [
        Service(name="Physiotherapy", duration_minutes=60, price=100.0),
        Service(name="Wound Dressing", duration_minutes=30, price=50.0),
        Service(name="Medication Admin", duration_minutes=15, price=25.0),
    ]
    
    # Caregivers
    caregivers = [
        Caregiver(name="Alice Johnson", specialization="Physiotherapy"),
        Caregiver(name="Bob Smith", specialization="Wound Care"),
        Caregiver(name="Carol Davis", specialization="General Care"),
    ]
    
    # Patient
    patient = Patient(name="John Patient", contact="john@example.com")
    
    # Add and commit
    test_db.add_all(services)
    test_db.add_all(caregivers)
    test_db.add(patient)
    test_db.commit()
    
    # Refresh to get IDs
    for s in services:
        test_db.refresh(s)
    for c in caregivers:
        test_db.refresh(c)
    test_db.refresh(patient)
    
    # Create service-caregiver relationships
    # Service 0 (Physiotherapy) -> caregivers 0, 2
    services[0].caregivers.append(caregivers[0])
    services[0].caregivers.append(caregivers[2])
    
    # Service 1 (Wound Dressing) -> caregivers 1, 2
    services[1].caregivers.append(caregivers[1])
    services[1].caregivers.append(caregivers[2])
    
    # Service 2 (Medication Admin) -> caregiver 2
    services[2].caregivers.append(caregivers[2])
    
    test_db.commit()
    
    return {
        "services": services,
        "caregivers": caregivers,
        "patient": patient,
    }
