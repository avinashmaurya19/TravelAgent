"""Deterministic flight details retrieval tool."""

from typing import Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.repositories.flight_repo import FlightRepository


class GetFlightDetailsArgs(BaseModel):
    """Arguments for retrieving flight details."""
    flight_id: str = Field(..., description="Flight UUID or flight number (e.g. AI-559, 6E-204)")


def get_flight_details_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve full details for a flight using UUID or flight number."""
    args = GetFlightDetailsArgs.model_validate(arguments)
    repo = FlightRepository(db)
    flight = repo.get_by_id(args.flight_id)

    if not flight:
        return {
            "status": "not_found",
            "message": f"Flight with identifier '{args.flight_id}' not found.",
        }

    return {
        "status": "success",
        "flight": {
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
        },
    }
