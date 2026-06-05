"""
Tests for slot availability endpoint.
"""

from datetime import datetime
from app.models import Booking


def test_get_available_slots_empty(client, seed_data):
    """
    Test: Get available slots when no bookings exist.
    Expected: All 15-min aligned slots for the day should be available.
    """
    service_id = seed_data["services"][0].id  # Physiotherapy (60 min)
    caregiver_id = seed_data["caregivers"][0].id
    date = "2024-01-15"
    
    response = client.get(
        f"/slots/available?service_id={service_id}&date={date}&caregiver_id={caregiver_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["service_id"] == service_id
    assert data["date"] == date
    assert data["service_name"] == "Physiotherapy"
    assert data["duration_minutes"] == 60
    assert len(data["available_slots"]) > 0
    
    # Check that all slots are 60 minutes apart
    for slot in data["available_slots"]:
        start = datetime.fromisoformat(slot["start_time"])
        end = datetime.fromisoformat(slot["end_time"])
        duration = (end - start).total_seconds() / 60
        assert duration == 60


def test_get_available_slots_with_existing_booking(client, test_db, seed_data):
    """
    Test: Get available slots when a booking already exists.
    Expected: Slot should be excluded from availability.
    
    Scenario:
    - Book caregiver A for 10:00-11:00 (60 min)
    - Query available slots
    - 10:00-11:00 should NOT appear
    """
    service = seed_data["services"][0]  # Physiotherapy (60 min)
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    date = "2024-01-15"
    booked_start = datetime(2024, 1, 15, 10, 0, 0)
    booked_end = datetime(2024, 1, 15, 11, 0, 0)
    
    # Create a booking
    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=booked_start,
        end_time=booked_end,
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    # Query available slots
    response = client.get(
        f"/slots/available?service_id={service.id}&date={date}&caregiver_id={caregiver.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that 10:00 slot is not available
    available_starts = [
        datetime.fromisoformat(slot["start_time"])
        for slot in data["available_slots"]
    ]
    
    assert booked_start not in available_starts
    
    # But other slots should be available (e.g., 9:00, 11:00, etc.)
    assert datetime(2024, 1, 15, 9, 0, 0) in available_starts
    assert datetime(2024, 1, 15, 11, 0, 0) in available_starts


def test_get_available_slots_global_booking_hidden_for_other_caregiver(client, test_db, seed_data):
    """
    Test: A booked time is hidden for every caregiver.

    Scenario:
    - Caregiver A has a 10:00-11:00 booking
    - Query availability for caregiver B on the same date

    Expected:
    - 10:00-11:00 should NOT appear at all
    """
    service = seed_data["services"][0]
    caregiver_a = seed_data["caregivers"][0]
    caregiver_b = seed_data["caregivers"][1]
    patient = seed_data["patient"]
    date = "2024-01-15"

    booking = Booking(
        service_id=service.id,
        caregiver_id=caregiver_a.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 15, 10, 0, 0),
        end_time=datetime(2024, 1, 15, 11, 0, 0),
        price=service.price,
    )
    test_db.add(booking)
    test_db.commit()

    response = client.get(
        f"/slots/available?service_id={service.id}&date={date}&caregiver_id={caregiver_b.id}"
    )

    assert response.status_code == 200
    data = response.json()

    available_starts = [
        datetime.fromisoformat(slot["start_time"])
        for slot in data["available_slots"]
    ]

    assert datetime(2024, 1, 15, 10, 0, 0) not in available_starts


def test_get_available_slots_15min_alignment(client, seed_data):
    """
    Test: Slots are correctly aligned to 15-minute boundaries.
    Expected: All slot start times should be on :00, :15, :30, or :45 minutes.
    """
    service_id = seed_data["services"][1].id  # Wound Dressing (30 min)
    caregiver_id = seed_data["caregivers"][1].id
    date = "2024-01-16"
    
    response = client.get(
        f"/slots/available?service_id={service_id}&date={date}&caregiver_id={caregiver_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check alignment
    for slot in data["available_slots"]:
        start = datetime.fromisoformat(slot["start_time"])
        minute = start.minute
        
        # Should be 0, 15, 30, or 45
        assert minute in [0, 15, 30, 45], f"Slot at {start} not aligned to 15-min boundary"


def test_get_available_slots_service_not_found(client):
    """
    Test: Query for non-existent service.
    Expected: 404 error.
    """
    response = client.get("/slots/available?service_id=99999&date=2024-01-15&caregiver_id=1")
    assert response.status_code == 404


def test_get_available_slots_respects_service_duration(client, test_db, seed_data):
    """
    Test: Slot availability respects service duration.
    
    Scenario:
    - Service A: 60 min
    - Service B: 30 min
    - Booking: Service A, 10:00-11:00
    - Query Service B: 10:30-11:00 should NOT be available (conflicts with Service A)
    """
    service_60 = seed_data["services"][0]  # 60 min
    service_30 = seed_data["services"][1]  # 30 min
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    date = "2024-01-17"
    
    # Book 60-min service from 10:00-11:00
    booking = Booking(
        service_id=service_60.id,
        caregiver_id=caregiver.id,
        patient_id=patient.id,
        start_time=datetime(2024, 1, 17, 10, 0, 0),
        end_time=datetime(2024, 1, 17, 11, 0, 0),
        price=service_60.price,
    )
    test_db.add(booking)
    test_db.commit()
    
    # Query 30-min service
    response = client.get(
        f"/slots/available?service_id={service_30.id}&date={date}&caregiver_id={caregiver.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    available_starts = [
        datetime.fromisoformat(slot["start_time"])
        for slot in data["available_slots"]
    ]
    
    # 10:00 (conflicts) and 10:15 (would end at 10:45, but 60-min booking goes until 11:00)
    # and 10:30 (would end at 11:00, blocked by 60-min booking) should all be blocked
    assert datetime(2024, 1, 17, 10, 0, 0) not in available_starts
    assert datetime(2024, 1, 17, 10, 15, 0) not in available_starts
    assert datetime(2024, 1, 17, 10, 30, 0) not in available_starts
    
    # But 11:00 should be available (no conflict)
    assert datetime(2024, 1, 17, 11, 0, 0) in available_starts
