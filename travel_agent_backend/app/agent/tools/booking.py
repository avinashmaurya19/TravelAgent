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
    contact_email: Optional[str] = Field(default="guest@travelagent.ai", description="Contact email address")
    contact_phone: Optional[str] = Field(default="9999999999", description="Contact mobile number")


def create_booking_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create a pending booking reservation awaiting explicit human confirmation."""
    args = CreateBookingArgs.model_validate(arguments)
    service = BookingService(db)

    # 1. Resolve flight by UUID or flight number
    flight = service.flight_repo.get_by_id(args.flight_id)
    if not flight:
        return {
            "status": "error",
            "error": "FlightNotFound",
            "message": f"Flight '{args.flight_id}' could not be found in our inventory.",
        }

    # 2. Pre-booking seat availability re-check guardrail
    passengers_count = len(args.passengers)
    if not service.flight_repo.check_seat_availability(flight.id, passengers_count):
        return {
            "status": "error",
            "error": "InsufficientSeats",
            "available_seats": flight.available_seats,
            "requested_passengers": passengers_count,
            "message": (
                f"Only {flight.available_seats} seat(s) remaining on flight {flight.flight_number}. "
                f"Cannot book for {passengers_count} passenger(s)."
            ),
        }

    # 3. Create pending booking via service
    req = BookingCreateRequest(
        flight_id=flight.id,
        passengers=args.passengers,
        add_extra_baggage=args.add_extra_baggage,
        seat_selection_tier=args.seat_selection,
        contact_email=args.contact_email or "guest@travelagent.ai",
        contact_phone=args.contact_phone or "9999999999",
    )

    booking = service.create_pending_booking(req)

    flight_data = {
        "id": flight.id,
        "flight_number": flight.flight_number,
        "airline": flight.airline,
        "origin": flight.origin,
        "destination": flight.destination,
        "departure_time": flight.departure_time.isoformat(),
        "arrival_time": flight.arrival_time.isoformat(),
        "duration_minutes": flight.duration_minutes,
        "stops": flight.stops,
        "cabin_class": flight.cabin_class,
        "price": flight.price,
        "available_seats": flight.available_seats,
    }

    return {
        "status": "pending_confirmation",
        "booking_id": booking.id,
        "booking_reference": booking.booking_reference,
        "total_price": booking.total_price,
        "base_fare": booking.base_fare,
        "tax_amount": booking.tax_amount,
        "baggage_fee": booking.baggage_fee,
        "seat_fee": booking.seat_fee,
        "currency": "INR",
        "passengers_count": booking.passengers_count,
        "flight": flight_data,
        "human_confirmation_required": True,
        "message": (
            f"Pre-booking checks passed ({flight.available_seats} seats verified). "
            f"Reservation initiated in PENDING state with PNR {booking.booking_reference}. "
            f"Total payable: ₹{booking.total_price:.2f} (Base: ₹{booking.base_fare:.2f}, Taxes: ₹{booking.tax_amount:.2f}). "
            "Please present this to the user for explicit confirmation before booking is finalized."
        ),
    }
