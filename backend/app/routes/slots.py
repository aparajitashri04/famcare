from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Service, Booking, Patient
from app.schemas import (
    AvailableSlotsResponse,
    AvailableSlot,
    ServiceResponse,
    CaregiverResponse,
    PatientResponse,
    PatientCreate,
)

router = APIRouter(prefix="/slots", tags=["slots"])


@router.get("/services", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    """
    List all available services.
    
    Returns all services with duration and price information.
    """
    services = db.query(Service).all()
    return [ServiceResponse.model_validate(s) for s in services]


@router.get("/caregivers-for-service/{service_id}", response_model=list[CaregiverResponse])
def get_caregivers_for_service(service_id: int, db: Session = Depends(get_db)):
    """
    List all caregivers qualified to provide a specific service.
    
    Path Parameters:
        service_id: ID of the service
    
    Returns:
        List of caregivers who are qualified for this service
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
    
    return [CaregiverResponse.model_validate(c) for c in service.caregivers]


@router.get("/patients", response_model=list[PatientResponse])
def list_patients(db: Session = Depends(get_db)):
    """
    List all patients (for development/testing).
    
    In production, this would be protected/filtered based on user role.
    """
    patients = db.query(Patient).all()
    return [PatientResponse.model_validate(p) for p in patients]


@router.post("/patients", response_model=PatientResponse, status_code=201)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    """
    Create a patient record for the current user flow.

    If a matching patient already exists by name or contact, return that record
    instead of creating a duplicate.
    """
    existing = db.query(Patient).filter(
        (Patient.name == payload.name) | (Patient.contact == payload.contact)
    ).first()
    if existing:
        return PatientResponse.model_validate(existing)

    patient = Patient(name=payload.name, contact=payload.contact)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return PatientResponse.model_validate(patient)


def get_15min_slots_for_date(date_str: str, service_duration_minutes: int) -> list:
    """
    Generate all 15-minute aligned slots for a given date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        service_duration_minutes: Duration of the service
    
    Returns:
        List of (start_time, end_time) tuples for all possible 15-min aligned slots
    """
    # Parse date
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # Start from 9:00 AM, end at 6:00 PM (reasonable business hours)
    day_start = datetime.combine(date_obj, datetime.min.time()).replace(hour=9, minute=0)
    day_end = datetime.combine(date_obj, datetime.min.time()).replace(hour=18, minute=0)
    
    slots = []
    current = day_start
    duration = timedelta(minutes=service_duration_minutes)
    
    while current + duration <= day_end:
        end_time = current + duration
        slots.append((current, end_time))
        # Move to next 15-minute slot
        current += timedelta(minutes=15)
    
    return slots


def get_booked_slots_for_date(
    db: Session,
    date_str: str
) -> list:
    """
    Get all booked time ranges on a date.

    Booked times are treated as global reservations, so any overlap should
    block the slot regardless of caregiver.
    
    Returns list of (start_time, end_time) tuples for booked slots.
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    day_start = datetime.combine(date_obj, datetime.min.time())
    day_end = datetime.combine(date_obj, datetime.max.time())
    
    booked = db.query(Booking).filter(
        Booking.start_time >= day_start,
        Booking.start_time < day_end,
    ).all()
    
    return [(b.start_time, b.end_time) for b in booked]


def slot_conflicts_with_booked(
    slot_start: datetime,
    slot_end: datetime,
    booked_slots: list
) -> bool:
    """
    Check if a proposed slot conflicts with any booked slots.
    
    OVERLAP LOGIC:
        slot.start < booked.end  AND  slot.end > booked.start
    """
    for booked_start, booked_end in booked_slots:
        if slot_start < booked_end and slot_end > booked_start:
            return True
    return False


@router.get("/available", response_model=AvailableSlotsResponse)
def get_available_slots(
    service_id: int,
    date: str,  # YYYY-MM-DD
    caregiver_id: int = None,
    patient_id: int = 1,  # Default to 1 if not provided, but can be overridden
    db: Session = Depends(get_db),
):
    """
    Get available 15-minute aligned slots for a service on a given date.
    
    If caregiver_id is provided, return only slots available for that specific caregiver.
    Otherwise, return one entry per globally available slot using any qualified caregiver.
    
    Query Parameters:
        service_id (required): ID of the service
        date (required): Date in YYYY-MM-DD format
        caregiver_id (optional): Specific caregiver ID
        patient_id (optional): Patient ID (defaults to 1)
    
    Response:
        AvailableSlotsResponse containing list of available (start_time, end_time) slots
    """
    
    # Validate service exists
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail=f"Service {service_id} not found")
    
    # Generate all 15-min slots for this date
    all_slots = get_15min_slots_for_date(date, service.duration_minutes)
    
    if not all_slots:
        return AvailableSlotsResponse(
            service_id=service_id,
            date=date,
            service_name=service.name,
            duration_minutes=service.duration_minutes,
            available_slots=[],
        )
    
    booked = get_booked_slots_for_date(db, date)

    # If caregiver_id specified, check availability for that specific caregiver
    if caregiver_id:
        # Verify caregiver is qualified for this service
        qualified = any(c.id == caregiver_id for c in service.caregivers)
        if not qualified:
            raise HTTPException(
                status_code=400,
                detail=f"Caregiver {caregiver_id} does not provide service {service_id}"
            )

        available = [
            AvailableSlot(
                start_time=start,
                end_time=end,
                service_id=service_id,
                caregiver_id=caregiver_id,
            )
            for start, end in all_slots
            if not slot_conflicts_with_booked(start, end, booked)
        ]
    else:
        # No specific caregiver - return unique globally available time slots.
        qualified_caregiver_ids = [c.id for c in service.caregivers]
        available = []

        if qualified_caregiver_ids:
            for slot_start, slot_end in all_slots:
                if slot_conflicts_with_booked(slot_start, slot_end, booked):
                    continue

                available.append(
                    AvailableSlot(
                        start_time=slot_start,
                        end_time=slot_end,
                        service_id=service_id,
                        caregiver_id=qualified_caregiver_ids[0],
                    )
                )
    
    return AvailableSlotsResponse(
        service_id=service_id,
        date=date,
        service_name=service.name,
        duration_minutes=service.duration_minutes,
        available_slots=available,
    )
