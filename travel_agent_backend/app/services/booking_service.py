"""Service layer orchestrating the booking lifecycle and human confirmation."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database.models import BookingModel, BookingStatus
from app.database.repositories.flight_repo import FlightRepository
from app.database.repositories.booking_repo import BookingRepository
from app.services.fare_calculator import FareCalculator
from app.schemas.booking import BookingCreateRequest


class BookingService:
    """Orchestrates booking workflows and inventory safety guardrails."""

    def __init__(self, db: Session):
        self.db = db
        self.flight_repo = FlightRepository(db)
        self.booking_repo = BookingRepository(db)

    def create_pending_booking(self, req: BookingCreateRequest) -> BookingModel:
        """Create a pending booking after verifying flight seat inventory."""
        flight = self.flight_repo.get_by_id(req.flight_id)
        if not flight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flight with ID {req.flight_id} not found",
            )

        passengers_count = len(req.passengers)
        if not self.flight_repo.check_seat_availability(req.flight_id, passengers_count):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient seats available. Requested: {passengers_count}, Available: {flight.available_seats}",
            )

        # Calculate exact deterministic fare
        fare_details = FareCalculator.calculate(
            flight=flight,
            passengers_count=passengers_count,
            add_extra_baggage=req.add_extra_baggage,
            seat_selection=req.seat_selection_tier or "standard",
        )

        passengers_data = [p.model_dump() for p in req.passengers]

        booking = self.booking_repo.create_pending_booking(
            flight_id=req.flight_id,
            base_fare=fare_details["total_base_fare"],
            tax_amount=fare_details["tax_amount"],
            baggage_fee=fare_details["baggage_fee"],
            seat_fee=fare_details["seat_fee"],
            total_price=fare_details["total_amount"],
            contact_email=req.contact_email,
            contact_phone=req.contact_phone,
            passengers_data=passengers_data,
            user_id=req.user_id,
        )

        return booking

    def get_booking(self, booking_id: str) -> BookingModel:
        """Fetch booking by ID or raise 404."""
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with ID {booking_id} not found",
            )
        return booking

    def confirm_booking(self, booking_id: str) -> BookingModel:
        """Explicit confirmation step: Re-checks seat availability and reserves seats."""
        booking = self.get_booking(booking_id)

        if booking.status == BookingStatus.CONFIRMED:
            return booking

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot confirm a cancelled booking",
            )

        # Dual-check availability guardrail
        if not self.flight_repo.check_seat_availability(booking.flight_id, booking.passengers_count):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Seats are no longer available for this flight",
            )

        # Atomically deduct seats
        success = self.flight_repo.decrement_seats(booking.flight_id, booking.passengers_count)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Failed to allocate seats for booking confirmation",
            )

        confirmed_booking = self.booking_repo.confirm_booking(booking_id)
        return confirmed_booking

    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel booking, restore inventory, and calculate refund."""
        booking = self.get_booking(booking_id)

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled",
            )

        was_confirmed = booking.status == BookingStatus.CONFIRMED

        # Release seats if previously confirmed
        if was_confirmed:
            self.flight_repo.increment_seats(booking.flight_id, booking.passengers_count)

        self.booking_repo.cancel_booking(booking_id)

        # Fixed cancellation fee calculation (e.g., ₹1500 per pax if confirmed)
        cancellation_fee = 1500.0 * booking.passengers_count if was_confirmed else 0.0
        refund_amount = max(0.0, booking.total_price - cancellation_fee) if was_confirmed else 0.0

        return {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "status": BookingStatus.CANCELLED.value,
            "refund_amount": refund_amount,
            "cancellation_fee": cancellation_fee,
            "message": "Booking successfully cancelled",
        }
