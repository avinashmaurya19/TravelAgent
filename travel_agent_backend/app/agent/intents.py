"""Pydantic schemas for agent intent recognition and entity extraction."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class IntentType(str, Enum):
    """Categorical classification of user travel requests."""
    SEARCH_FLIGHT = "SEARCH_FLIGHT"
    REFINE_SEARCH = "REFINE_SEARCH"
    FLIGHT_DETAILS = "FLIGHT_DETAILS"
    COMPARE_FLIGHTS = "COMPARE_FLIGHTS"
    SELECT_FLIGHT = "SELECT_FLIGHT"
    BOOK_FLIGHT = "BOOK_FLIGHT"
    CHECK_BOOKING = "CHECK_BOOKING"
    CANCEL_BOOKING = "CANCEL_BOOKING"
    TRAVEL_POLICY = "TRAVEL_POLICY"
    GENERAL_TRAVEL = "GENERAL_TRAVEL"


class AgentIntent(BaseModel):
    """Structured representation of parsed user intent and travel constraints."""
    intent: IntentType = Field(
        ...,
        description="The primary action the user is attempting to perform",
    )
    origin: Optional[str] = Field(
        default=None,
        description="Origin airport 3-letter IATA code, e.g. DEL, BOM",
    )
    destination: Optional[str] = Field(
        default=None,
        description="Destination airport 3-letter IATA code, e.g. BOM, BLR, GOI",
    )
    date: Optional[str] = Field(
        default=None,
        description="Departure date expression, e.g. '2026-09-06', 'tomorrow', 'this Saturday'",
    )
    passengers: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Number of adult passengers",
    )
    cabin_class: Optional[str] = Field(
        default="economy",
        description="Cabin class: 'economy', 'premium_economy', or 'business'",
    )
    max_price: Optional[float] = Field(
        default=None,
        description="Maximum budget/price cap in INR per passenger",
    )
    max_stops: Optional[int] = Field(
        default=None,
        description="Maximum layover stops (0 for non-stop / direct flights)",
    )
    preferred_airline: Optional[str] = Field(
        default=None,
        description="Filter by specific airline name (e.g. 'IndiGo', 'Air India', 'SpiceJet')",
    )
    flight_number_or_id: Optional[str] = Field(
        default=None,
        description="Flight number code (e.g. 'AI-559') or UUID if specified",
    )
    booking_reference: Optional[str] = Field(
        default=None,
        description="PNR booking reference code or UUID if querying or cancelling",
    )
    policy_topic: Optional[str] = Field(
        default=None,
        description="Policy subject (e.g. 'baggage', 'refund', 'cancellation', 'checkin')",
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Reasoning behind the extracted intent and parameters",
    )

    @field_validator("origin", "destination", mode="before")
    @classmethod
    def uppercase_airport_codes(cls, v: Optional[str]) -> Optional[str]:
        """Ensure airport codes are uppercase 3-letter codes."""
        if v and isinstance(v, str):
            clean = v.strip().upper()
            return clean if len(clean) == 3 else v
        return v
