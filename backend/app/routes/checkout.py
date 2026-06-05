from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CheckoutRequest, CheckoutSuccess, CheckoutFailure
from app.services.checkout_service import (
    process_checkout,
    OverlapDetectionError,
    InvalidSlotError,
)

router = APIRouter(prefix="/cart", tags=["checkout"])


@router.post("/checkout")
def checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
):
    """
    Atomic checkout endpoint.
    
    Accepts a list of booking requests with a patient ID.
    If ALL bookings are valid and no conflicts exist, creates them all in a single transaction.
    If ANY booking fails (overlap, invalid slot, etc.), rolls back ENTIRE transaction.
    No partial bookings.
    
    Request Body:
    {
        "patient_id": 1,
        "bookings": [
            {
                "service_id": 1,
                "caregiver_id": 1,
                "start_time": "2024-01-15T10:00:00",
                "date": "2024-01-15"
            },
            ...
        ]
    }
    
    Response (Success):
    {
        "success": true,
        "message": "3 bookings confirmed",
        "bookings": [...],
        "total_price": 150.00
    }
    
    Response (Failure):
    {
        "success": false,
        "message": "Checkout failed",
        "failed_booking_index": 1,
        "reason": "Caregiver 2 has conflict between 2024-01-15 14:00:00 and 2024-01-15 15:00:00"
    }
    """
    
    try:
        # Process checkout - atomically creates all bookings or rolls back
        bookings = process_checkout(
            db=db,
            patient_id=request.patient_id,
            booking_requests=request.bookings,
        )
        
        # Calculate total price
        total_price = sum(b.price for b in bookings)
        
        return CheckoutSuccess(
            success=True,
            message=f"{len(bookings)} booking(s) confirmed",
            bookings=bookings,
            total_price=total_price,
        )
    
    except OverlapDetectionError as e:
        # Extract which booking failed from the error message
        error_msg = str(e)
        failed_idx = 0
        
        # Parse "Booking X:" from error message
        if "Booking" in error_msg:
            try:
                failed_idx = int(error_msg.split("Booking ")[1].split(":")[0])
            except (IndexError, ValueError):
                failed_idx = 0
        
        # Auto-rollback due to exception context
        db.rollback()
        
        return CheckoutFailure(
            success=False,
            message="Checkout failed - conflict detected",
            failed_booking_index=failed_idx,
            reason=error_msg,
        )
    
    except InvalidSlotError as e:
        # Auto-rollback due to exception context
        db.rollback()
        
        return CheckoutFailure(
            success=False,
            message="Checkout failed - invalid slot",
            failed_booking_index=0,
            reason=str(e),
        )
    
    except Exception as e:
        # Unexpected error - rollback
        db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during checkout: {str(e)}",
        )