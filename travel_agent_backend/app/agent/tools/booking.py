"""Deterministic booking tool enforcing human-in-the-loop pending reservation."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.schemas.booking import BookingCreateRequest, PassengerCreate
from app.services.booking_service import BookingService


class CreateBookingArgs(BaseModel):
    """Arguments for creating a pending flight reservation."""
    flight_id: str = Field(..., description="Flight UUID or flight number (e.g. AI-559)")
    passengers: List[PassengerCreate] = Field(..., description="List of passenger names, ages, and genders")
    add_extra_baggage: bool = Field(default=False, description="Add 15kg extra baggage")
    seat_selection: Optional[str] = Field(default="standard", description="Seat tier: standard, extra_legroom, premium")
    contact_email: Optional[str] = Field(default=None, description="Contact email address")
    contact_phone: Optional[str] = Field(default=None, description="Contact mobile number")


def create_booking_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create a pending booking reservation awaiting explicit human confirmation."""
    args = CreateBookingArgs.model_validate(arguments)
    service = BookingService(db)

    req = BookingCreateRequest(
        flight_id=args.flight_id,
        passengers=args.passengers,
        add_extra_baggage=args.add_extra_baggage,
        seat_selection_tier=args.seat_selection,
        contact_email=args.contact_email or "guest@travelagent.ai",
        contact_phone=args.contact_phone or "9999999999",
    )

    booking = service.create_pending_booking(req)

    return {
        "status": "pending_confirmation",
        "booking_id": booking.id,
        "booking_reference": booking.booking_reference,
        "total_price": booking.total_price,
        "human_confirmation_required": True,
        "message": (
            f"Reservation created in PENDING state with PNR {booking.bookingReference if hasattr(booking, 'bookingReference') else booking.booking_reference}. "
            f"Total payable: ₹{booking.total_price:.2f}. "
            "Please present this to the user for explicit confirmation before booking is finalized."
        ),
    }
