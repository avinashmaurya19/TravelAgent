"""Deterministic seat availability checking tool."""

from typing import Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.repositories.flight_repo import FlightRepository


class CheckAvailabilityArgs(BaseModel):
    """Arguments for seat availability verification."""
    flight_id: str = Field(..., description="Flight UUID or flight number (e.g. AI-559)")
    passengers: int = Field(default=1, ge=1, le=9, description="Number of seats required")


def check_availability_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Verify seat inventory for requested passengers."""
    args = CheckAvailabilityArgs.model_validate(arguments)
    repo = FlightRepository(db)
    flight = repo.get_by_id(args.flight_id)

    if not flight:
        return {
            "status": "error",
            "is_available": False,
            "message": f"Flight '{args.flight_id}' does not exist.",
        }

    is_avail = flight.available_seats >= args.passengers
    return {
        "status": "success",
        "flight_id": flight.id,
        "flight_number": flight.flight_number,
        "available_seats": flight.available_seats,
        "requested_passengers": args.passengers,
        "is_available": is_avail,
        "message": (
            f"{flight.available_seats} seats available."
            if is_avail
            else f"Only {flight.available_seats} seats remaining, requested {args.passengers}."
        ),
    }
