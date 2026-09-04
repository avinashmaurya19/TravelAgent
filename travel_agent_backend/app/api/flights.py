"""Flight API router for flight search, details, availability, and fare calculation."""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.repositories.flight_repo import FlightRepository
from app.services.fare_calculator import FareCalculator
from app.schemas.flight import (
    FlightResponse,
    FareBreakdownRequest,
    FareBreakdownResponse,
    AvailabilityResponse,
)

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("/search", response_model=List[FlightResponse])
def search_flights(
    origin: str = Query(..., description="Origin 3-letter airport code (e.g. DEL)", min_length=3, max_length=3),
    destination: str = Query(..., description="Destination 3-letter airport code (e.g. BOM)", min_length=3, max_length=3),
    departure_date: date = Query(..., description="Departure date (YYYY-MM-DD)"),
    passengers: int = Query(default=1, ge=1, le=9, description="Number of passengers"),
    cabin_class: Optional[str] = Query(default="economy", description="Cabin class: economy, premium_economy, business"),
    max_price: Optional[float] = Query(default=None, description="Maximum price per passenger"),
    max_stops: Optional[int] = Query(default=None, description="Maximum layover stops (0=direct)"),
    preferred_airline: Optional[str] = Query(default=None, description="Airline name filter"),
    sort_by: Optional[str] = Query(default="price_asc", description="Sort order: price_asc, price_desc, duration_asc, departure_asc"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Search for flights matching route, date, and user constraints."""
    repo = FlightRepository(db)
    flights = repo.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        passengers=passengers,
        cabin_class=cabin_class,
        max_price=max_price,
        max_stops=max_stops,
        preferred_airline=preferred_airline,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )
    return flights


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight_details(
    flight_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve detailed information for a specific flight."""
    repo = FlightRepository(db)
    flight = repo.get_by_id(flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found",
        )
    return flight


@router.get("/{flight_id}/availability", response_model=AvailabilityResponse)
def check_flight_availability(
    flight_id: str,
    passengers: int = Query(default=1, ge=1, le=9),
    db: Session = Depends(get_db),
):
    """Check if requested number of seats are available on the flight."""
    repo = FlightRepository(db)
    flight = repo.get_by_id(flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found",
        )

    is_available = flight.available_seats >= passengers
    message = (
        f"{flight.available_seats} seats available"
        if is_available
        else f"Only {flight.available_seats} seats left, requested {passengers}"
    )

    return AvailabilityResponse(
        flight_id=flight.id,
        available_seats=flight.available_seats,
        requested_passengers=passengers,
        is_available=is_available,
        message=message,
    )


@router.post("/fare-breakdown", response_model=FareBreakdownResponse)
def calculate_fare_breakdown(
    req: FareBreakdownRequest,
    db: Session = Depends(get_db),
):
    """Calculate transparent fare breakdown (base fare, 18% GST, baggage, and seat selection)."""
    repo = FlightRepository(db)
    flight = repo.get_by_id(req.flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {req.flight_id} not found",
        )

    fare_dict = FareCalculator.calculate(
        flight=flight,
        passengers_count=req.passengers_count,
        add_extra_baggage=req.add_extra_baggage,
        seat_selection=req.seat_selection or "standard",
    )
    return FareBreakdownResponse(**fare_dict)
