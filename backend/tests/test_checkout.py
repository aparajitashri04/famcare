"""
Tests for atomic checkout.
The most critical tests for this assignment.
"""

from datetime import datetime
from app.models import Booking


def test_checkout_single_booking_success(client, seed_data):
    """
    Test: Successful checkout with a single booking.
    Expected: Booking is created and returned.
    """
    service = seed_data["services"][0]  # Physiotherapy
    caregiver = seed_data["caregivers"][0]
    
    payload = {
        "bookings": [
            {
                "service_id": service.id,
                "caregiver_id": caregiver.id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            }
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["bookings"]) == 1
    
    booking = data["bookings"][0]
    assert booking["service_id"] == service.id
    assert booking["caregiver_id"] == caregiver.id
    assert booking["patient_id"] == 1  # Fixed patient
    assert booking["price"] == service.price
    
    # Check end_time is calculated correctly (start + duration)
    # 60-min service starting at 10:00 should end at 11:00
    start = datetime.fromisoformat(booking["start_time"])
    end = datetime.fromisoformat(booking["end_time"])
    duration = (end - start).total_seconds() / 60
    assert duration == 60


def test_checkout_multiple_bookings_success(client, seed_data):
    """
    Test: Successful checkout with multiple non-conflicting bookings.
    Expected: All 3 bookings created in single transaction.
    """
    services = seed_data["services"]
    caregivers = seed_data["caregivers"]
    
    payload = {
        "bookings": [
            {
                "service_id": services[0].id,  # Physiotherapy (60 min)
                "caregiver_id": caregivers[0].id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
            {
                "service_id": services[1].id,  # Wound Dressing (30 min)
                "caregiver_id": caregivers[1].id,
                "start_time": "2024-01-15T14:00:00",
                "date": "2024-01-15",
            },
            {
                "service_id": services[0].id,  # Physiotherapy (60 min)
                "caregiver_id": caregivers[2].id,
                "start_time": "2024-01-16T10:00:00",
                "date": "2024-01-16",
            },
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert len(data["bookings"]) == 3
    
    # Verify total price
    expected_total = services[0].price + services[1].price + services[0].price
    assert data["total_price"] == expected_total


def test_checkout_caregiver_overlap_rejected(client, test_db, seed_data):
    """
    Test: ATOMIC ROLLBACK - Caregiver overlap detected.
    
    Scenario:
    - Cart has 2 bookings
    - Booking 1: Caregiver A, 10:00-11:00 (succeeds)
    - Booking 2: Same caregiver A, 10:30-11:00 (overlaps with booking 1)
    
    Expected:
    - ENTIRE checkout fails
    - Neither booking is created (rollback)
    - Error message identifies which booking failed
    """
    service = seed_data["services"][0]  # 60 min
    caregiver = seed_data["caregivers"][0]
    
    payload = {
        "bookings": [
            {
                "service_id": service.id,
                "caregiver_id": caregiver.id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
            {
                "service_id": service.id,
                "caregiver_id": caregiver.id,  # SAME CAREGIVER
                "start_time": "2024-01-15T10:30:00",  # OVERLAPS
                "date": "2024-01-15",
            },
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Checkout should fail
    assert data["success"] is False
    assert data["message"] == "Checkout failed - conflict detected"
    assert "Caregiver" in data["reason"]
    
    # Verify NO bookings were created (atomic rollback)
    bookings = test_db.query(Booking).all()
    assert len(bookings) == 0, "ATOMIC ROLLBACK FAILED: Bookings were partially created!"


def test_checkout_global_slot_overlap_rejected(client, test_db, seed_data):
    """
    Test: ATOMIC ROLLBACK - Global slot overlap detected.

    Scenario:
    - Booking 1: Caregiver A, 10:00-11:00
    - Booking 2: Different caregiver B, same 10:00-11:00 window

    Expected:
    - Entire checkout fails
    - No bookings are created
    """
    service = seed_data["services"][0]  # 60 min
    caregiver_a = seed_data["caregivers"][0]
    caregiver_b = seed_data["caregivers"][1]

    payload = {
        "bookings": [
            {
                "service_id": service.id,
                "caregiver_id": caregiver_a.id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
            {
                "service_id": service.id,
                "caregiver_id": caregiver_b.id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
        ]
    }

    response = client.post("/cart/checkout", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is False
    assert data["message"] == "Checkout failed - conflict detected"
    assert "already booked" in data["reason"]

    bookings = test_db.query(Booking).all()
    assert len(bookings) == 0, "ATOMIC ROLLBACK FAILED: Bookings were partially created!"


def test_checkout_duplicate_slot_in_same_payload_rejected(client, test_db, seed_data):
    """
    Test: Duplicate slot in the same checkout payload is rejected.

    Scenario:
    - Booking 1: 10:00-11:00
    - Booking 2: 10:00-11:00 in the same request

    Expected:
    - Entire checkout fails
    - No bookings are created
    """
    services = seed_data["services"]
    caregivers = seed_data["caregivers"]

    payload = {
        "bookings": [
            {
                "service_id": services[0].id,
                "caregiver_id": caregivers[0].id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
            {
                "service_id": services[1].id,
                "caregiver_id": caregivers[1].id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
        ]
    }

    response = client.post("/cart/checkout", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is False
    assert data["message"] == "Checkout failed - conflict detected"
    assert "already booked" in data["reason"]

    bookings = test_db.query(Booking).all()
    assert len(bookings) == 0, "ATOMIC ROLLBACK FAILED: Bookings were partially created!"


def test_checkout_patient_overlap_rejected(client, test_db, seed_data):
    """
    Test: ATOMIC ROLLBACK - Patient overlap detected.
    
    Scenario:
    - Cart has 2 bookings for same patient
    - Booking 1: Patient, Service A (60 min), 10:00-11:00
    - Booking 2: Same patient, Service B (30 min), 10:30-11:00 (patient conflict)
    
    Expected:
    - ENTIRE checkout fails
    - Neither booking is created (rollback)
    """
    services = seed_data["services"]
    caregivers = seed_data["caregivers"]
    
    payload = {
        "bookings": [
            {
                "service_id": services[0].id,  # 60 min
                "caregiver_id": caregivers[0].id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
            {
                "service_id": services[1].id,  # 30 min
                "caregiver_id": caregivers[1].id,
                "start_time": "2024-01-15T10:30:00",  # OVERLAPS with booking 1
                "date": "2024-01-15",
            },
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Checkout should fail
    assert data["success"] is False
    assert "Patient" in data["reason"]
    
    # Verify NO bookings were created
    bookings = test_db.query(Booking).all()
    assert len(bookings) == 0, "ATOMIC ROLLBACK FAILED: Bookings were partially created!"


def test_checkout_invalid_service(client, test_db, seed_data):
    """
    Test: ATOMIC ROLLBACK - Non-existent service.
    
    Scenario:
    - Cart has 2 bookings
    - Booking 1: Valid service
    - Booking 2: Invalid service_id (99999)
    
    Expected:
    - ENTIRE checkout fails
    - Booking 1 is NOT created (rollback)
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    
    payload = {
        "bookings": [
            {
                "service_id": service.id,
                "caregiver_id": caregiver.id,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
            {
                "service_id": 99999,  # INVALID
                "caregiver_id": caregiver.id,
                "start_time": "2024-01-15T14:00:00",
                "date": "2024-01-15",
            },
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Checkout should fail
    assert data["success"] is False
    assert "does not exist" in data["reason"]
    
    # Verify NO bookings were created (including the first valid one)
    bookings = test_db.query(Booking).all()
    assert len(bookings) == 0, "ATOMIC ROLLBACK FAILED: Booking 1 was created despite checkout failure!"


def test_checkout_invalid_caregiver(client, test_db, seed_data):
    """
    Test: ATOMIC ROLLBACK - Non-existent caregiver.
    
    Scenario:
    - Cart has 1 booking with invalid caregiver
    
    Expected:
    - Checkout fails
    - No bookings created
    """
    service = seed_data["services"][0]
    
    payload = {
        "bookings": [
            {
                "service_id": service.id,
                "caregiver_id": 99999,  # INVALID
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15",
            },
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is False
    assert "does not exist" in data["reason"]
    
    bookings = test_db.query(Booking).all()
    assert len(bookings) == 0

