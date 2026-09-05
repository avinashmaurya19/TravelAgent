"""Pydantic schemas for Booking creation, confirmation, and management."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.schemas.flight import FlightResponse


class PassengerSchema(BaseModel):
    """Passenger details schema."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Passenger first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Passenger last name")
    age: int = Field(..., ge=1, le=120, description="Passenger age")
    gender: str = Field(..., description="Gender (e.g., Male, Female, Other)")
    seat_number: Optional[str] = Field(default=None, description="Assigned seat code, e.g. 12A")

    model_config = ConfigDict(from_attributes=True)


PassengerCreate = PassengerSchema


class BookingCreateRequest(BaseModel):
    """Request schema for initiating a pending flight booking."""
    flight_id: str = Field(..., description="Target flight UUID")
    user_id: Optional[str] = Field(default=None, description="Optional associated user UUID")
    contact_email: EmailStr = Field(..., description="Primary contact email for e-ticket")
    contact_phone: str = Field(..., min_length=10, max_length=15, description="Primary contact phone number")
    passengers: List[PassengerSchema] = Field(..., min_length=1, max_length=9, description="List of passengers")
    add_extra_baggage: bool = Field(default=False, description="Add 15kg extra baggage")
    seat_selection_tier: Optional[str] = Field(default="standard", description="standard, extra_legroom, premium")


class BookingConfirmRequest(BaseModel):
    """Request schema for explicitly confirming a pending booking."""
    payment_method: Optional[str] = Field(default="UPI", description="Mock payment method: UPI, CARD, NETBANKING")


class BookingResponse(BaseModel):
    """Booking details response schema."""
    id: str
    booking_reference: str
    flight_id: str
    user_id: Optional[str]
    status: str
    passengers_count: int
    base_fare: float
    tax_amount: float
    baggage_fee: float
    seat_fee: float
    total_price: float
    contact_email: Optional[str]
    contact_phone: Optional[str]
    flight: Optional[FlightResponse] = None
    passengers: List[PassengerSchema] = []
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BookingCancelResponse(BaseModel):
    """Booking cancellation response."""
    booking_id: str
    booking_reference: str
    status: str
    refund_amount: float
    cancellation_fee: float
    message: str
