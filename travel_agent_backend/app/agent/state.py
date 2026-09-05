"""TravelState Pydantic model for maintaining structured conversational request state."""

from datetime import date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class TravelState(BaseModel):
    """Encapsulates the ongoing structured travel request parameters across dialog turns."""
    origin: Optional[str] = Field(
        default=None,
        description="3-letter origin airport code (e.g. DEL, BOM)",
    )
    destination: Optional[str] = Field(
        default=None,
        description="3-letter destination airport code (e.g. BOM, BLR, GOI)",
    )
    departure_date: Optional[str] = Field(
        default=None,
        description="Departure date (YYYY-MM-DD or relative like 'tomorrow')",
    )
    passengers: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Number of adult passengers",
    )
    cabin_class: str = Field(
        default="economy",
        description="Cabin class: 'economy', 'premium_economy', 'business'",
    )
    max_price: Optional[float] = Field(
        default=None,
        description="Maximum budget cap in INR per passenger",
    )
    max_stops: Optional[int] = Field(
        default=None,
        description="Maximum stops allowed (0 for non-stop)",
    )
    preferred_airline: Optional[str] = Field(
        default=None,
        description="Preferred airline name (e.g. 'IndiGo', 'Air India')",
    )
    selected_flight_id: Optional[str] = Field(
        default=None,
        description="UUID or flight code of user's selected flight",
    )
    passenger_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Collected passenger info for pending reservation",
    )
    booking_id: Optional[str] = Field(
        default=None,
        description="UUID of created booking in database",
    )
    booking_reference: Optional[str] = Field(
        default=None,
        description="PNR reference code of booking",
    )
    last_search_flight_ids: List[str] = Field(
        default_factory=list,
        description="List of flight UUIDs returned in the most recent search",
    )

    def update_from_intent(self, intent_data: Dict[str, Any]) -> None:
        """Update active state with non-null attributes from an extracted intent."""
        for key in [
            "origin", "destination", "passengers", "cabin_class",
            "max_price", "max_stops", "preferred_airline"
        ]:
            val = intent_data.get(key)
            if val is not None:
                setattr(self, key, val)

        if intent_data.get("date") is not None:
            self.departure_date = str(intent_data["date"])
