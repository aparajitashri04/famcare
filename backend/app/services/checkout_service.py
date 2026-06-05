from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app.models import Booking, Service, Caregiver, Patient
from app.schemas import BookingRequest, BookingResponse


class OverlapDetectionError(Exception):
    """Raised when overlap is detected"""
    pass


class InvalidSlotError(Exception):
    """Raised when slot is invalid"""
    pass


def check_caregiver_overlap(
    db: Session,
    caregiver_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int = None
) -> bool:
    """
    Check if caregiver has overlapping bookings.
    
    OVERLAP LOGIC:
    Two intervals [A_start, A_end) and [B_start, B_end) overlap if:
        A_start < B_end  AND  A_end > B_start
    
    Query: Find any existing booking where:
        existing.start_time < new_end_time  AND  existing.end_time > new_start_time
    
    Args:
        db: Database session
        caregiver_id: Caregiver ID to check
        start_time: Requested slot start
        end_time: Requested slot end
        exclude_booking_id: Booking ID to exclude (for updates)
    
    Returns:
        True if overlap found, False if slot is free
    """
    query = db.query(Booking).filter(
        Booking.caregiver_id == caregiver_id,
        Booking.start_time < end_time,  # existing.start < new.end
        Booking.end_time > start_time,  # existing.end > new.start
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.first() is not None


def check_global_overlap(
    db: Session,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int = None
) -> bool:
    """
    Check if any booking overlaps the requested time window.

    This is the global slot lock: once a time range is booked, no other booking
    should be allowed to use the same overlapping window, regardless of
    caregiver or patient.
    """
    query = db.query(Booking).filter(
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )

    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)

    return query.first() is not None


def overlaps_with_bookings(
    start_time: datetime,
    end_time: datetime,
    bookings: list[Booking],
) -> bool:
    """
    Check whether a proposed time window overlaps any booking in a list.

    This is used to detect conflicts between bookings staged in the same
    checkout request before they are committed to the database.
    """
    for booking in bookings:
        if start_time < booking.end_time and end_time > booking.start_time:
            return True
    return False


def check_patient_overlap(
    db: Session,
    patient_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: int = None
) -> bool:
    """
    Check if patient has overlapping bookings on the same day.
    
    OVERLAP LOGIC (same as caregiver):
        existing.start_time < new_end_time  AND  existing.end_time > new_start_time
    
    Args:
        db: Database session
        patient_id: Patient ID to check
        start_time: Requested slot start
        end_time: Requested slot end
        exclude_booking_id: Booking ID to exclude (for updates)
    
    Returns:
        True if overlap found, False if slot is free
    """
    query = db.query(Booking).filter(
        Booking.patient_id == patient_id,
        Booking.start_time < end_time,  # existing.start < new.end
        Booking.end_time > start_time,  # existing.end > new.start
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.first() is not None


def validate_service_exists(db: Session, service_id: int) -> Service:
    """Validate that service exists and return it"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise InvalidSlotError(f"Service {service_id} does not exist")
    return service


def validate_caregiver_exists(db: Session, caregiver_id: int) -> Caregiver:
    """Validate that caregiver exists and return it"""
    caregiver = db.query(Caregiver).filter(Caregiver.id == caregiver_id).first()
    if not caregiver:
        raise InvalidSlotError(f"Caregiver {caregiver_id} does not exist")
    return caregiver


def validate_patient_exists(db: Session, patient_id: int) -> Patient:
    """Validate that patient exists and return it"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise InvalidSlotError(f"Patient {patient_id} does not exist")
    return patient


def process_checkout(
    db: Session,
    patient_id: int,
    booking_requests: List[BookingRequest]
) -> List[BookingResponse]:
    """
    ATOMIC CHECKOUT LOGIC
    
    This function runs in a single database transaction.
    If ANY booking fails validation or conflicts, the ENTIRE transaction rolls back.
    No partial bookings.
    
    Steps:
    1. Validate all services and caregivers exist
    2. For each booking:
       a. Fetch service to get duration
       b. Calculate end_time = start_time + duration
       c. Check global slot overlap
       d. Check caregiver overlap
       e. Check patient overlap
       f. If any conflict, raise exception (triggers rollback)
    3. Create all booking records (if we reach here, all validations passed)
    4. Commit transaction
    
    Args:
        db: Database session (will auto-rollback on exception)
        patient_id: Patient making the booking
        booking_requests: List of booking requests from cart
    
    Returns:
        List of created BookingResponse objects
    
    Raises:
        OverlapDetectionError: If caregiver or patient overlap detected
        InvalidSlotError: If service/caregiver doesn't exist or slot invalid
    """
    
    # Step 1: Validate patient exists
    validate_patient_exists(db, patient_id)
    
    # Pre-fetch all services and caregivers to validate existence
    service_ids = set(br.service_id for br in booking_requests)
    caregiver_ids = set(br.caregiver_id for br in booking_requests)
    
    services = {s.id: s for s in db.query(Service).filter(Service.id.in_(service_ids)).all()}
    caregivers = {c.id: c for c in db.query(Caregiver).filter(Caregiver.id.in_(caregiver_ids)).all()}
    
    # Validate all services exist
    for service_id in service_ids:
        if service_id not in services:
            raise InvalidSlotError(f"Service {service_id} does not exist")
    
    # Validate all caregivers exist
    for caregiver_id in caregiver_ids:
        if caregiver_id not in caregivers:
            raise InvalidSlotError(f"Caregiver {caregiver_id} does not exist")
    
    # Step 2 & 3: Validate each booking and prepare for creation
    bookings_to_create = []
    
    for idx, booking_request in enumerate(booking_requests):
        service = services[booking_request.service_id]
        
        # Calculate end time based on service duration
        start_time = booking_request.start_time
        duration = timedelta(minutes=service.duration_minutes)
        end_time = start_time + duration

        # Global slot lock: no other booking may use this time window
        if check_global_overlap(db, start_time, end_time) or overlaps_with_bookings(start_time, end_time, bookings_to_create):
            raise OverlapDetectionError(
                f"Booking {idx}: Slot between {start_time} and {end_time} is already booked"
            )
        
        # Check caregiver overlap
        if check_caregiver_overlap(db, booking_request.caregiver_id, start_time, end_time):
            raise OverlapDetectionError(
                f"Booking {idx}: Caregiver {booking_request.caregiver_id} has conflict "
                f"between {start_time} and {end_time}"
            )
        
        # Check patient overlap
        if check_patient_overlap(db, patient_id, start_time, end_time):
            raise OverlapDetectionError(
                f"Booking {idx}: Patient has conflicting booking "
                f"between {start_time} and {end_time}"
            )
        
        # Build booking object (not yet flushed/committed)
        booking = Booking(
            service_id=booking_request.service_id,
            caregiver_id=booking_request.caregiver_id,
            patient_id=patient_id,
            start_time=start_time,
            end_time=end_time,
            price=service.price,
        )
        bookings_to_create.append(booking)
    
    # Step 4: If we reach here, all validations passed - create bookings
    for booking in bookings_to_create:
        db.add(booking)
    
    # Step 5: Commit transaction (atomically)
    db.commit()
    
    # Refresh all bookings to get IDs and created_at
    for booking in bookings_to_create:
        db.refresh(booking)
    
    return [BookingResponse.model_validate(b) for b in bookings_to_create]
