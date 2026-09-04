"""Pydantic schemas for Flight data and search operations."""

from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class FlightBase(BaseModel):
    """Base flight schema."""
    flight_number: str = Field(..., description="IATA flight number, e.g. 6E-204")
    airline: str = Field(..., description="Operating airline name, e.g. IndiGo")
    origin: str = Field(..., description="Origin airport code, e.g. DEL")
    destination: str = Field(..., description="Destination airport code, e.g. BOM")
    departure_time: datetime = Field(..., description="Flight departure timestamp")
    arrival_time: datetime = Field(..., description="Flight arrival timestamp")
    duration_minutes: int = Field(..., description="Total flight duration in minutes")
    stops: int = Field(default=0, description="Number of layovers (0 for direct)")
    stops_details: Optional[List[Any]] = Field(default=None, description="Details of layover stops")
    cabin_class: str = Field(default="economy", description="Cabin class: economy, premium_economy, business")
    price: float = Field(..., description="Base ticket price in INR")
    available_seats: int = Field(default=100, description="Remaining available seats")


class FlightResponse(FlightBase):
    """Flight response schema with ID."""
    id: str = Field(..., description="Unique flight UUID")

    model_config = ConfigDict(from_attributes=True)


class FlightSearchQuery(BaseModel):
    """Query parameters for searching flights."""
    origin: str = Field(..., description="Origin 3-letter airport code (e.g. DEL)", min_length=3, max_length=3)
    destination: str = Field(..., description="Destination 3-letter airport code (e.g. BOM)", min_length=3, max_length=3)
    departure_date: date = Field(..., description="Departure date (YYYY-MM-DD)")
    passengers: int = Field(default=1, ge=1, le=9, description="Number of passengers")
    cabin_class: Optional[str] = Field(default="economy", description="Cabin class filter")
    max_price: Optional[float] = Field(default=None, description="Maximum budget per ticket")
    max_stops: Optional[int] = Field(default=None, description="Maximum stops allowed")
    preferred_airline: Optional[str] = Field(default=None, description="Filter by preferred airline name")
    sort_by: Optional[str] = Field(default="price_asc", description="Sort order: price_asc, price_desc, duration_asc, departure_asc")


class FareBreakdownRequest(BaseModel):
    """Request schema for calculating detailed flight fare."""
    flight_id: str = Field(..., description="Flight identifier")
    passengers_count: int = Field(default=1, ge=1, le=9, description="Number of passengers")
    add_extra_baggage: bool = Field(default=False, description="Add 15kg extra baggage per passenger")
    seat_selection: Optional[str] = Field(default="standard", description="Seat tier: standard, extra_legroom, premium")


class FareBreakdownResponse(BaseModel):
    """Detailed fare breakdown response."""
    flight_id: str
    flight_number: str
    airline: str
    passengers_count: int
    base_fare_per_passenger: float
    total_base_fare: float
    tax_rate_percentage: float = 18.0
    tax_amount: float
    baggage_fee: float
    seat_fee: float
    total_amount: float
    currency: str = "INR"


class AvailabilityResponse(BaseModel):
    """Flight seat availability response."""
    flight_id: str
    available_seats: int
    requested_passengers: int
    is_available: bool
    message: str
