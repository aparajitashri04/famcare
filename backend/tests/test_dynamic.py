"""
Tests for dynamic discovery endpoints.
"""



def test_list_services(client, seed_data):
    """
    Test: List all available services.
    Expected: Returns all services with their details.
    """
    response = client.get("/slots/services")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 3
    
    service_names = {s["name"] for s in data}
    assert "Physiotherapy" in service_names
    assert "Wound Dressing" in service_names
    assert "Medication Admin" in service_names
    
    # Check service details
    phys = next(s for s in data if s["name"] == "Physiotherapy")
    assert phys["duration_minutes"] == 60
    assert phys["price"] == 100.0


def test_get_caregivers_for_service(client, seed_data):
    """
    Test: Get caregivers qualified for a specific service.
    Expected: Returns only caregivers assigned to that service.
    
    Setup:
    - Physiotherapy (service 1) -> Alice, Carol
    - Wound Dressing (service 2) -> Bob, Carol
    - Medication Admin (service 3) -> Carol
    """
    phys_service = seed_data["services"][0]
    
    response = client.get(f"/slots/caregivers-for-service/{phys_service.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2  # Alice and Carol
    
    caregiver_names = {c["name"] for c in data}
    assert "Alice Johnson" in caregiver_names
    assert "Carol Davis" in caregiver_names
    assert "Bob Smith" not in caregiver_names  # Bob doesn't do Physiotherapy


def test_get_caregivers_for_medication_admin(client, seed_data):
    """
    Test: Medication Admin service only has Carol as qualified caregiver.
    """
    med_service = seed_data["services"][2]
    
    response = client.get(f"/slots/caregivers-for-service/{med_service.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["name"] == "Carol Davis"


def test_get_caregivers_invalid_service(client):
    """
    Test: Request caregivers for non-existent service.
    Expected: 404 error.
    """
    response = client.get("/slots/caregivers-for-service/99999")
    assert response.status_code == 404


def test_list_patients(client, seed_data):
    """
    Test: List all patients.
    Expected: Returns all patients.
    """
    response = client.get("/slots/patients")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["name"] == "John Patient"
    assert data[0]["id"] == 1


def test_slot_availability_now_returns_qualified_caregivers(client, seed_data):
    """
    Test: Slot availability endpoint now returns only qualified caregivers.
    
    Setup:
    - Request slots for Physiotherapy (service 1)
    - Only Alice and Carol are qualified
    """
    phys_service = seed_data["services"][0]
    date = "2024-01-20"
    
    # Get available slots without specifying caregiver
    response = client.get(f"/slots/available?service_id={phys_service.id}&date={date}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["available_slots"]) > 0
    
    # Check that all caregivers are either Alice or Carol
    caregiver_ids = {slot["caregiver_id"] for slot in data["available_slots"]}
    
    alice = seed_data["caregivers"][0]
    carol = seed_data["caregivers"][2]
    bob = seed_data["caregivers"][1]
    
    assert alice.id in caregiver_ids or carol.id in caregiver_ids
    assert bob.id not in caregiver_ids  # Bob doesn't do Physiotherapy


def test_checkout_now_accepts_patient_id(client, seed_data):
    """
    Test: Checkout endpoint now accepts patient_id in request.
    Expected: Can specify which patient is booking.
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    patient = seed_data["patient"]
    
    payload = {
        "patient_id": patient.id,
        "bookings": [
            {
                "service_id": service.id,
                "caregiver_id": caregiver.id,
                "start_time": "2024-01-25T10:00:00",
                "date": "2024-01-25",
            }
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["bookings"][0]["patient_id"] == patient.id


def test_checkout_defaults_patient_id_to_1(client, seed_data):
    """
    Test: If patient_id not provided, defaults to 1.
    """
    service = seed_data["services"][0]
    caregiver = seed_data["caregivers"][0]
    
    payload = {
        "bookings": [  # No patient_id specified
            {
                "service_id": service.id,
                "caregiver_id": caregiver.id,
                "start_time": "2024-01-26T10:00:00",
                "date": "2024-01-26",
            }
        ]
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["bookings"][0]["patient_id"] == 1  # Default patient
