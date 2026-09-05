"""Deterministic fare breakdown calculation tool."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.repositories.flight_repo import FlightRepository
from app.services.fare_calculator import FareCalculator


class CalculateFareArgs(BaseModel):
    """Arguments for fare breakdown calculation."""
    flight_id: str = Field(..., description="Flight UUID or flight number (e.g. AI-559)")
    passengers: int = Field(default=1, ge=1, le=9, description="Passenger count")
    add_extra_baggage: bool = Field(default=False, description="Add 15kg extra check-in luggage")
    seat_selection: Optional[str] = Field(default="standard", description="Seat tier: standard, extra_legroom, premium")


def calculate_fare_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate itemized fare breakdown (base fare, 18% GST, add-ons)."""
    args = CalculateFareArgs.model_validate(arguments)
    repo = FlightRepository(db)
    flight = repo.get_by_id(args.flight_id)

    if not flight:
        return {
            "status": "error",
            "message": f"Flight '{args.flight_id}' not found.",
        }

    fare_dict = FareCalculator.calculate(
        flight=flight,
        passengers_count=args.passengers,
        add_extra_baggage=args.add_extra_baggage,
        seat_selection=args.seat_selection or "standard",
    )

    return {
        "status": "success",
        "fare_breakdown": fare_dict,
    }
