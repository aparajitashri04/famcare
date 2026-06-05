from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class ServiceResponse(BaseModel):
    id: int
    name: str
    duration_minutes: int
    price: float
    
    class Config:
        from_attributes = True


class CaregiverResponse(BaseModel):
    id: int
    name: str
    specialization: str
    
    class Config:
        from_attributes = True


class PatientResponse(BaseModel):
    id: int
    name: str
    contact: str
    
    class Config:
        from_attributes = True


class PatientCreate(BaseModel):
    name: str
    contact: str


class AvailableSlot(BaseModel):
    """Represents a single available 15-min slot"""
    start_time: datetime
    end_time: datetime
    service_id: int
    caregiver_id: int


class AvailableSlotsResponse(BaseModel):
    """Response for GET /slots/available"""
    service_id: int
    date: str  # YYYY-MM-DD
    service_name: str
    duration_minutes: int
    available_slots: List[AvailableSlot]


class BookingRequest(BaseModel):
    """Single booking item in the checkout cart"""
    service_id: int
    caregiver_id: int
    start_time: datetime
    date: str  # YYYY-MM-DD (for reference, actual timing is in start_time)


class CheckoutRequest(BaseModel):
    """POST /cart/checkout"""
    patient_id: int = 1  # Defaults to 1 if not provided
    bookings: List[BookingRequest] = Field(..., min_items=1)


class BookingResponse(BaseModel):
    id: int
    service_id: int
    caregiver_id: int
    patient_id: int
    start_time: datetime
    end_time: datetime
    price: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class CheckoutSuccess(BaseModel):
    """Successful checkout response"""
    success: bool = True
    message: str
    bookings: List[BookingResponse]
    total_price: float


class CheckoutFailure(BaseModel):
    """Failed checkout response"""
    success: bool = False
    message: str
    failed_booking_index: int  # Which booking in the cart failed
    reason: str  # Why it failed (overlap, not available, etc.)
