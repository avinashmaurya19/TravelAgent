"""Booking repository for managing booking state and passenger manifests."""

import secrets
import string
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.database.models import BookingModel, BookingStatus, PassengerModel


class BookingRepository:
    """Data access methods for bookings and passengers."""

    def __init__(self, db: Session):
        self.db = db

    def generate_booking_reference(self) -> str:
        """Generate a unique 6-character alphanumeric PNR (e.g. TA78X9)."""
        chars = string.ascii_uppercase + string.digits
        while True:
            ref = "TA" + "".join(secrets.choice(chars) for _ in range(6))
            existing = self.db.query(BookingModel).filter(BookingModel.booking_reference == ref).first()
            if not existing:
                return ref

    def get_by_id(self, booking_id: str) -> Optional[BookingModel]:
        """Fetch booking by primary key UUID with relationships."""
        return (
            self.db.query(BookingModel)
            .options(joinedload(BookingModel.flight), joinedload(BookingModel.passengers))
            .filter(BookingModel.id == booking_id)
            .first()
        )

    def get_by_reference(self, reference: str) -> Optional[BookingModel]:
        """Fetch booking by 6-char booking reference code."""
        return (
            self.db.query(BookingModel)
            .options(joinedload(BookingModel.flight), joinedload(BookingModel.passengers))
            .filter(BookingModel.booking_reference == reference.upper())
            .first()
        )

    def create_pending_booking(
        self,
        flight_id: str,
        base_fare: float,
        tax_amount: float,
        baggage_fee: float,
        seat_fee: float,
        total_price: float,
        contact_email: str,
        contact_phone: str,
        passengers_data: List[dict],
        user_id: Optional[str] = None,
    ) -> BookingModel:
        """Create a new booking in PENDING state awaiting human confirmation."""
        booking_ref = self.generate_booking_reference()
        booking = BookingModel(
            booking_reference=booking_ref,
            user_id=user_id,
            flight_id=flight_id,
            status=BookingStatus.PENDING,
            base_fare=base_fare,
            tax_amount=tax_amount,
            baggage_fee=baggage_fee,
            seat_fee=seat_fee,
            total_price=total_price,
            passengers_count=len(passengers_data),
            contact_email=contact_email,
            contact_phone=contact_phone,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(booking)
        self.db.flush()

        for p in passengers_data:
            passenger = PassengerModel(
                booking_id=booking.id,
                first_name=p["first_name"],
                last_name=p["last_name"],
                age=p["age"],
                gender=p["gender"],
                seat_number=p.get("seat_number"),
            )
            self.db.add(passenger)

        self.db.commit()
        return self.get_by_id(booking.id)

    def confirm_booking(self, booking_id: str) -> Optional[BookingModel]:
        """Mark a pending booking as confirmed."""
        booking = self.get_by_id(booking_id)
        if not booking:
            return None
        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def cancel_booking(self, booking_id: str) -> Optional[BookingModel]:
        """Cancel a booking."""
        booking = self.get_by_id(booking_id)
        if not booking:
            return None
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(booking)
        return booking
