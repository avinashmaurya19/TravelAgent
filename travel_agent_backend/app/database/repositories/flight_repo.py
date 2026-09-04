"""Flight repository for querying and managing flight inventory."""

from datetime import date, datetime, time
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, asc, desc

from app.database.models import FlightModel


class FlightRepository:
    """Data access methods for flight records."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, flight_id: str) -> Optional[FlightModel]:
        """Fetch a single flight by its primary key UUID, with fallback to flight_number."""
        flight = self.db.query(FlightModel).filter(FlightModel.id == flight_id).first()
        if not flight:
            flight = self.db.query(FlightModel).filter(FlightModel.flight_number == flight_id.upper()).first()
        return flight

    def get_by_flight_number(self, flight_number: str) -> Optional[FlightModel]:
        """Fetch a flight by flight number."""
        return self.db.query(FlightModel).filter(FlightModel.flight_number == flight_number.upper()).first()

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        passengers: int = 1,
        cabin_class: Optional[str] = "economy",
        max_price: Optional[float] = None,
        max_stops: Optional[int] = None,
        preferred_airline: Optional[str] = None,
        sort_by: Optional[str] = "price_asc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[FlightModel]:
        """Search flights matching routing, date, and filter criteria."""
        start_of_day = datetime.combine(departure_date, time.min)
        end_of_day = datetime.combine(departure_date, time.max)

        filters = [
            FlightModel.origin == origin.upper(),
            FlightModel.destination == destination.upper(),
            FlightModel.departure_time >= start_of_day,
            FlightModel.departure_time <= end_of_day,
            FlightModel.available_seats >= passengers,
        ]

        if cabin_class:
            filters.append(FlightModel.cabin_class == cabin_class.lower())

        if max_price is not None:
            filters.append(FlightModel.price <= max_price)

        if max_stops is not None:
            filters.append(FlightModel.stops <= max_stops)

        if preferred_airline:
            filters.append(FlightModel.airline.ilike(f"%{preferred_airline}%"))

        query = self.db.query(FlightModel).filter(and_(*filters))

        # Apply sorting
        if sort_by == "price_desc":
            query = query.order_by(desc(FlightModel.price))
        elif sort_by == "duration_asc":
            query = query.order_by(asc(FlightModel.duration_minutes))
        elif sort_by == "departure_asc":
            query = query.order_by(asc(FlightModel.departure_time))
        else:  # default price_asc
            query = query.order_by(asc(FlightModel.price))

        return query.offset(offset).limit(limit).all()

    def check_seat_availability(self, flight_id: str, requested_seats: int) -> bool:
        """Verify if enough seats remain for a flight."""
        flight = self.get_by_id(flight_id)
        if not flight:
            return False
        return flight.available_seats >= requested_seats

    def decrement_seats(self, flight_id: str, seats: int) -> bool:
        """Atomically reduce available seats upon booking."""
        flight = self.get_by_id(flight_id)
        if not flight or flight.available_seats < seats:
            return False
        flight.available_seats -= seats
        self.db.commit()
        self.db.refresh(flight)
        return True

    def increment_seats(self, flight_id: str, seats: int) -> bool:
        """Restore seats upon booking cancellation."""
        flight = self.get_by_id(flight_id)
        if not flight:
            return False
        flight.available_seats += seats
        self.db.commit()
        self.db.refresh(flight)
        return True

    def bulk_create(self, flights: List[FlightModel]) -> None:
        """Insert a batch of flight records."""
        self.db.bulk_save_objects(flights)
        self.db.commit()
