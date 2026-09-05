"""Deterministic flight comparison tool for side-by-side evaluation."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.repositories.flight_repo import FlightRepository


class CompareFlightsArgs(BaseModel):
    """Validated arguments for compare_flights tool."""
    flight_ids: List[str] = Field(
        ...,
        description="List of 2 to 4 flight UUIDs or flight numbers (e.g. ['6E-204', 'AI-802']) to compare",
        min_length=2,
        max_length=4,
    )


def compare_flights_tool(db: Session, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute side-by-side comparison of 2-4 flights."""
    args = CompareFlightsArgs.model_validate(arguments)
    repo = FlightRepository(db)

    flights = []
    not_found = []

    for fid in args.flight_ids:
        flight = repo.get_by_id(fid)
        if flight:
            flights.append(flight)
        else:
            not_found.append(fid)

    if len(flights) < 2:
        return {
            "status": "error",
            "message": f"Could not find at least 2 flights to compare. Missing: {not_found}",
            "flights": [],
        }

    # Extract comparison attributes
    flight_details = []
    for f in flights:
        h, m = divmod(f.duration_minutes, 60)
        flight_details.append({
            "id": f.id,
            "flight_number": f.flight_number,
            "airline": f.airline,
            "origin": f.origin,
            "destination": f.destination,
            "departure_time": f.departure_time.isoformat(),
            "arrival_time": f.arrival_time.isoformat(),
            "duration_minutes": f.duration_minutes,
            "formatted_duration": f"{h}h {m}m",
            "stops": f.stops,
            "cabin_class": f.cabin_class,
            "price": f.price,
            "available_seats": f.available_seats,
        })

    cheapest = min(flight_details, key=lambda x: x["price"])
    most_expensive = max(flight_details, key=lambda x: x["price"])
    fastest = min(flight_details, key=lambda x: x["duration_minutes"])
    slowest = max(flight_details, key=lambda x: x["duration_minutes"])

    price_diff = most_expensive["price"] - cheapest["price"]
    time_diff = slowest["duration_minutes"] - fastest["duration_minutes"]

    summary_points = [
        f"Cheapest: {cheapest['flight_number']} ({cheapest['airline']}) at ₹{cheapest['price']:,.0f} (saves ₹{price_diff:,.0f} vs {most_expensive['flight_number']}).",
        f"Fastest: {fastest['flight_number']} ({fastest['airline']}) at {fastest['formatted_duration']} ({time_diff} mins quicker than {slowest['flight_number']}).",
    ]

    direct_flights = [f["flight_number"] for f in flight_details if f["stops"] == 0]
    if direct_flights:
        summary_points.append(f"Non-stop options: {', '.join(direct_flights)}.")

    return {
        "status": "success",
        "compared_count": len(flight_details),
        "cheapest_flight": cheapest["flight_number"],
        "fastest_flight": fastest["flight_number"],
        "max_price_savings": price_diff,
        "max_time_savings_minutes": time_diff,
        "summary": " ".join(summary_points),
        "flights": flight_details,
    }
