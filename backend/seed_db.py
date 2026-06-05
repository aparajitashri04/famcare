"""
Seed database with initial test data.
Run this after init_db.py

Usage:
    python seed_db.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models import Base, Booking, Caregiver, Patient, Service, service_caregiver_association

# Load backend/.env so the seed script uses the same database as the app.
load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/famcare")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()


def seed():
    """Populate database with test data."""
    Base.metadata.create_all(bind=engine)

    # Clear existing data
    db.execute(service_caregiver_association.delete())
    db.query(Booking).delete()
    db.query(Patient).delete()
    db.query(Caregiver).delete()
    db.query(Service).delete()

    # Create services - realistic home healthcare services
    services = [
        Service(name="Physiotherapy", duration_minutes=60, price=120.0),
        Service(name="Wound Dressing", duration_minutes=30, price=60.0),
        Service(name="Medication Administration", duration_minutes=15, price=35.0),
        Service(name="Elderly Care", duration_minutes=120, price=180.0),
        Service(name="Post-Operative Care", duration_minutes=45, price=90.0),
        Service(name="Nursing Checkup", duration_minutes=30, price=65.0),
    ]

    # Create caregivers - multiple per specialization
    caregivers = [
        Caregiver(name="Mary Johnson", specialization="Physiotherapy"),
        Caregiver(name="John Davis", specialization="Physiotherapy"),
        Caregiver(name="Alex Martinez", specialization="Wound Care"),
        Caregiver(name="Sarah Wilson", specialization="Wound Care"),
        Caregiver(name="Emma Brown", specialization="General Care"),
        Caregiver(name="David Lee", specialization="General Care"),
        Caregiver(name="Patricia Garcia", specialization="Elderly Care"),
        Caregiver(name="Michael Anderson", specialization="Elderly Care"),
        Caregiver(name="Jennifer Taylor", specialization="Post-Operative"),
        Caregiver(name="Robert Martinez", specialization="Nursing"),
    ]

    # Create patient (fixed patient_id = 1)
    patient = Patient(name="John Patient", contact="john@example.com")

    # Add to session
    db.add_all(services)
    db.add_all(caregivers)
    db.add(patient)

    # Commit first to get IDs
    db.commit()

    # Now create service-caregiver relationships
    # Every service has at least 2 caregivers.
    relationships = [
        # Physiotherapy: Mary, John
        (services[0].id, caregivers[0].id),
        (services[0].id, caregivers[1].id),
        # Wound Dressing: Alex, Sarah
        (services[1].id, caregivers[2].id),
        (services[1].id, caregivers[3].id),
        # Medication Administration: Emma, David
        (services[2].id, caregivers[4].id),
        (services[2].id, caregivers[5].id),
        # Elderly Care: Patricia, Michael
        (services[3].id, caregivers[6].id),
        (services[3].id, caregivers[7].id),
        # Post-Operative Care: Jennifer, Emma
        (services[4].id, caregivers[8].id),
        (services[4].id, caregivers[4].id),
        # Nursing Checkup: Robert, David
        (services[5].id, caregivers[9].id),
        (services[5].id, caregivers[5].id),
    ]

    for service_id, caregiver_id in relationships:
        service = next(s for s in services if s.id == service_id)
        caregiver = next(c for c in caregivers if c.id == caregiver_id)
        service.caregivers.append(caregiver)

    db.commit()

    print("Seeded database with:")
    print(f"  - {len(services)} services")
    print(f"  - {len(caregivers)} caregivers")
    print("  - 1 patient (ID=1)")
    print("\nServices:")
    for s in services:
        print(f"  [{s.id}] {s.name}: {s.duration_minutes}min @ ${s.price}")
    print("\nCaregivers:")
    for c in caregivers:
        print(f"  [{c.id}] {c.name} ({c.specialization})")
    print("\nService-Caregiver Relationships:")
    for service in services:
        caregiver_names = ", ".join([c.name for c in service.caregivers])
        print(f"  {service.name}: {caregiver_names}")
    print("\nPatient:")
    print(f"  [{patient.id}] {patient.name}")


if __name__ == "__main__":
    try:
        seed()
        print("\nDatabase seeded successfully")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
