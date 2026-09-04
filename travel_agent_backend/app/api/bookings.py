"""Booking API router for managing booking reservation and confirmation lifecycle."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.booking_service import BookingService
from app.schemas.booking import (
    BookingCreateRequest,
    BookingConfirmRequest,
    BookingResponse,
    BookingCancelResponse,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    req: BookingCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new booking in PENDING state (awaiting explicit human confirmation)."""
    service = BookingService(db)
    booking = service.create_pending_booking(req)
    return booking


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_details(
    booking_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve details and status for a specific booking."""
    service = BookingService(db)
    booking = service.get_booking(booking_id)
    return booking


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
def confirm_booking(
    booking_id: str,
    req: BookingConfirmRequest = BookingConfirmRequest(),
    db: Session = Depends(get_db),
):
    """Confirm a pending booking (Human-in-the-loop confirmation guardrail)."""
    service = BookingService(db)
    confirmed = service.confirm_booking(booking_id)
    return confirmed


@router.post("/{booking_id}/cancel", response_model=BookingCancelResponse)
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
):
    """Cancel a booking and release reserved flight inventory."""
    service = BookingService(db)
    result = service.cancel_booking(booking_id)
    return BookingCancelResponse(**result)
