"""Deterministic flight filtering and ranking tool."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.repositories.flight_repo import FlightRepository
from .flight_search import _resolve_departure_date


class FilterFlightsArgs(BaseModel):
    """Arguments for filtering and refining flight results."""
    origin: str = Field(..., description="3-letter IATA origin airport code")
    destination: str = Field(..., description="3-letter IATA destination airport code")
    departure_date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD or 'tomorrow'")
    max_price: Optional[float] = Field(default=None, description="Price ceiling in INR")
    max_stops: Optional[int] = Field(default=None, description="Max layovers (0 for direct flights)")
    preferred_airline: Optional[str] = Field(default=None, description="Airline name filter")
    sort_by: Optional[str] = Field(default="price_asc", description="Sort: price_asc, price_desc, duration_asc")


def filter_flights_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Re-query flights applying strict filter criteria and sorting."""
    args = FilterFlightsArgs.model_validate(arguments)
    parsed_date = _resolve_departure_date(args.departure_date)

    repo = FlightRepository(db)
    results = repo.search_flights(
        origin=args.origin.upper(),
        destination=args.destination.upper(),
        departure_date=parsed_date,
        max_price=args.max_price,
        max_stops=args.max_stops,
        preferred_airline=args.preferred_airline,
        sort_by=args.sort_by,
        limit=5,
    )

    flight_list: List[Dict[str, Any]] = []
    for f in results:
        flight_list.append({
            "id": f.id,
            "flight_number": f.flight_number,
            "airline": f.airline,
            "origin": f.origin,
            "destination": f.destination,
            "departure_time": f.departure_time.isoformat(),
            "arrival_time": f.arrival_time.isoformat(),
            "duration_minutes": f.duration_minutes,
            "stops": f.stops,
            "cabin_class": f.cabin_class,
            "price": f.price,
            "available_seats": f.available_seats,
        })

    return {
        "status": "success",
        "filtered_count": len(flight_list),
        "flights": flight_list,
    }
