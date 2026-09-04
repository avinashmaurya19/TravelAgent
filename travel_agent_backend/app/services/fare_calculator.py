"""Deterministic fare calculation service."""

from typing import Dict, Any
from app.database.models import FlightModel


class FareCalculator:
    """Calculates granular pricing breakdowns for flights."""

    GST_TAX_RATE = 0.18  # 18% Aviation GST
    EXTRA_BAGGAGE_FEE = 1200.0  # ₹1200 per 15kg extra baggage per passenger
    SEAT_FEES = {
        "standard": 0.0,
        "extra_legroom": 600.0,
        "premium": 1200.0,
    }

    @classmethod
    def calculate(
        cls,
        flight: FlightModel,
        passengers_count: int = 1,
        add_extra_baggage: bool = False,
        seat_selection: str = "standard",
    ) -> Dict[str, Any]:
        """Compute full fare breakdown deterministically."""
        base_fare_per_pax = float(flight.price)
        total_base_fare = base_fare_per_pax * passengers_count

        # Calculate GST
        tax_amount = round(total_base_fare * cls.GST_TAX_RATE, 2)

        # Baggage fee
        baggage_fee = (cls.EXTRA_BAGGAGE_FEE * passengers_count) if add_extra_baggage else 0.0

        # Seat selection fee
        seat_tier = (seat_selection or "standard").lower()
        seat_rate = cls.SEAT_FEES.get(seat_tier, 0.0)
        seat_fee = seat_rate * passengers_count

        total_amount = round(total_base_fare + tax_amount + baggage_fee + seat_fee, 2)

        return {
            "flight_id": flight.id,
            "flight_number": flight.flight_number,
            "airline": flight.airline,
            "passengers_count": passengers_count,
            "base_fare_per_passenger": base_fare_per_pax,
            "total_base_fare": total_base_fare,
            "tax_rate_percentage": cls.GST_TAX_RATE * 100,
            "tax_amount": tax_amount,
            "baggage_fee": baggage_fee,
            "seat_fee": seat_fee,
            "total_amount": total_amount,
            "currency": "INR",
        }
