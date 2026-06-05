"""
Tests for overlap detection.
Verifies correct interval overlap logic: new_start < existing_end AND new_end > existing_start
"""

from datetime import datetime
from app.models import Booking
from app.services.checkout_service import check_caregiver_overlap, check_patient_overlap


def test_overlap_exact_same_time(test_db, seed_data):
    """
    Test: Exact same time overlap.
    - Existing: 10:00-11:00
    - New: 10:00-11:00
    Expected: Overlap detected
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    # Create existing booking
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    # Check for overlap
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 10, 0, 0),
        datetime(2024, 1, 15, 11, 0, 0),
    )
    
    assert overlaps is True


def test_overlap_partial_overlap_start(test_db, seed_data):
    """
    Test: Partial overlap - new starts during existing.
    - Existing: 10:00-11:00
    - New: 10:30-11:30
    Expected: Overlap detected
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 10, 30, 0),
        datetime(2024, 1, 15, 11, 30, 0),
    )
    
    assert overlaps is True


def test_overlap_partial_overlap_end(test_db, seed_data):
    """
    Test: Partial overlap - new ends during existing.
    - Existing: 10:00-11:00
    - New: 09:30-10:30
    Expected: Overlap detected ?
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 9, 30, 0),
        datetime(2024, 1, 15, 10, 30, 0),
    )
    
    assert overlaps is True


def test_overlap_contained(test_db, seed_data):
    """
    Test: New slot completely contained within existing.
    - Existing: 10:00-11:00
    - New: 10:15-10:45
    Expected: Overlap detected ?
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 10, 15, 0),
        datetime(2024, 1, 15, 10, 45, 0),
    )
    
    assert overlaps is True


def test_overlap_contains(test_db, seed_data):
    """
    Test: New slot completely contains existing.
    - Existing: 10:00-11:00
    - New: 09:00-12:00
    Expected: Overlap detected ?
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 9, 0, 0),
        datetime(2024, 1, 15, 12, 0, 0),
    )
    
    assert overlaps is True


def test_no_overlap_before(test_db, seed_data):
    """
    Test: No overlap - new slot entirely before existing.
    - Existing: 10:00-11:00
    - New: 09:00-10:00
    Expected: NO overlap ?
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 9, 0, 0),
        datetime(2024, 1, 15, 10, 0, 0),
    )
    
    assert overlaps is False


def test_no_overlap_after(test_db, seed_data):
    """
    Test: No overlap - new slot entirely after existing.
    - Existing: 10:00-11:00
    - New: 11:00-12:00
    Expected: NO overlap ?
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 11, 0, 0),
        datetime(2024, 1, 15, 12, 0, 0),
    )
    
    assert overlaps is False


def test_patient_overlap_detection(test_db, seed_data):
    """
    Test: Patient overlap detection works separately from caregiver overlap.
    - Different caregivers, same patient
    - Existing: 10:00-11:00 (Caregiver A)
    - New: 10:30-11:30 (Caregiver B)
    Expected: Patient overlap detected ?
    """
    service = seed_data["services"][0]
    caregivers = seed_data["caregivers"]
    patient = seed_data["patient"]
    
    # Booking with Caregiver A
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregivers[0].id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    # Check patient overlap with different caregiver
    overlaps = check_patient_overlap(
        test_db,
        patient.id,
        datetime(2024, 1, 15, 10, 30, 0),
        datetime(2024, 1, 15, 11, 30, 0),
    )
    
    assert overlaps is True


def test_different_caregivers_no_conflict(test_db, seed_data):
    """
    Test: Same time slot, different caregivers, no conflict.
    - Existing: 10:00-11:00 (Caregiver A)
    - New: 10:00-11:00 (Caregiver B)
    Expected: NO caregiver overlap (different caregivers) ?
    """
    service = seed_data["services"][0]
    caregivers = seed_data["caregivers"]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregivers[0].id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    # Check overlap for different caregiver
    overlaps = check_caregiver_overlap(
        test_db,
        caregivers[1].id,  # Different caregiver
        datetime(2024, 1, 15, 10, 0, 0),
        datetime(2024, 1, 15, 11, 0, 0),
    )
    
    assert overlaps is False


def test_off_by_one_minute_no_overlap(test_db, seed_data):
    """
    Test: Off by one minute - should NOT overlap.
    - Existing: 10:00-11:00
    - New: 11:00:00 (starts exactly when existing ends)
    Expected: NO overlap ?
    
    This tests the boundary: new_start >= existing_end
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    overlaps = check_caregiver_overlap(
        test_db,
        caregiver.id,
        datetime(2024, 1, 15, 11, 0, 0),
        datetime(2024, 1, 15, 12, 0, 0),
    )
    
    assert overlaps is False

