"""Deterministic flight search tool for the agent orchestrator."""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.repositories.flight_repo import FlightRepository


class SearchFlightsArgs(BaseModel):
    """Validated arguments for the search_flights tool."""
    origin: str = Field(..., description="3-letter IATA airport code, e.g. DEL, BOM", min_length=3, max_length=3)
    destination: str = Field(..., description="3-letter IATA airport code, e.g. BOM, BLR, GOI", min_length=3, max_length=3)
    departure_date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format or 'tomorrow'")
    passengers: int = Field(default=1, ge=1, le=9, description="Number of adult passengers")
    cabin_class: Optional[str] = Field(default="economy", description="Cabin class: economy, premium_economy, business")
    max_price: Optional[float] = Field(default=None, description="Maximum price in INR per passenger")
    max_stops: Optional[int] = Field(default=None, description="Maximum layovers (0 for direct flights)")
    preferred_airline: Optional[str] = Field(default=None, description="Airline name filter (e.g. IndiGo, Air India)")
    limit: int = Field(default=5, ge=1, le=20, description="Max number of flight options to return")


def _resolve_departure_date(date_str: Optional[str]) -> date:
    """Parse departure date string or resolve relative phrases, auto-correcting past years."""
    today = date.today()
    if not date_str:
        return today

    clean = date_str.strip().lower()
    if clean == "today":
        return today
    elif clean == "tomorrow":
        return today + timedelta(days=1)
    elif clean == "day after tomorrow":
        return today + timedelta(days=2)
    elif "next week" in clean or "any date" in clean or "any day" in clean:
        return today

    try:
        parsed = date.fromisoformat(date_str[:10])
        # Auto-correct past years from LLM training cutoff (e.g. 2024 -> current year 2026)
        if parsed.year < today.year:
            parsed = parsed.replace(year=today.year)
        if parsed < today:
            parsed = parsed.replace(year=today.year + 1)
        return parsed
    except (ValueError, OverflowError):
        # Fallback to today if unstructured date was supplied
        return today


def search_flights_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute flight search through the deterministic FlightRepository."""
    args = SearchFlightsArgs.model_validate(arguments)
    parsed_date = _resolve_departure_date(args.departure_date)

    repo = FlightRepository(db)
    results = repo.search_flights(
        origin=args.origin.upper(),
        destination=args.destination.upper(),
        departure_date=parsed_date,
        passengers=args.passengers,
        cabin_class=args.cabin_class,
        max_price=args.max_price,
        max_stops=args.max_stops,
        preferred_airline=args.preferred_airline,
        limit=args.limit,
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
        "origin": args.origin.upper(),
        "destination": args.destination.upper(),
        "departure_date": parsed_date.isoformat(),
        "count": len(flight_list),
        "flights": flight_list,
    }
