"""Integration tests for Booking Agent, pre-booking verification, and HITL lifecycle."""

import pytest
from app.agent.tools.booking import create_booking_tool
from app.database.models import FlightModel


def test_create_booking_tool_pending_state(db_session):
    """Test create_booking_tool creates a PENDING reservation with pre-booking checks."""
    args = {
        "flight_id": "flight-del-bom-1",
        "passengers": [
            {"first_name": "Rohan", "last_name": "Gupta", "age": 29, "gender": "Male"}
        ],
        "add_extra_baggage": False,
        "seat_selection": "standard",
    }
    result = create_booking_tool(db_session, args)

    assert result["status"] == "pending_confirmation"
    assert result["human_confirmation_required"] is True
    assert result["booking_reference"].startswith("TA")
    assert result["passengers_count"] == 1
    assert result["base_fare"] == 4500.0
    assert result["tax_amount"] == 810.0  # 18% GST
    assert result["total_price"] == 5310.0
    assert "flight" in result
    assert result["flight"]["flight_number"] == "6E-204"


def test_create_booking_tool_flight_not_found(db_session):
    """Test create_booking_tool handles non-existent flight cleanly."""
    args = {
        "flight_id": "non-existent-flight-id",
        "passengers": [
            {"first_name": "Jane", "last_name": "Doe", "age": 25, "gender": "Female"}
        ],
    }
    result = create_booking_tool(db_session, args)
    assert result["status"] == "error"
    assert result["error"] == "FlightNotFound"
    assert "could not be found" in result["message"]


def test_create_booking_tool_insufficient_seats(db_session):
    """Test create_booking_tool intercepts requests exceeding available seats."""
    # flight-del-bom-lowseats has only 2 seats
    args = {
        "flight_id": "flight-del-bom-lowseats",
        "passengers": [
            {"first_name": "P1", "last_name": "L1", "age": 20, "gender": "Male"},
            {"first_name": "P2", "last_name": "L2", "age": 21, "gender": "Female"},
            {"first_name": "P3", "last_name": "L3", "age": 22, "gender": "Male"},
        ],
    }
    result = create_booking_tool(db_session, args)
    assert result["status"] == "error"
    assert result["error"] == "InsufficientSeats"
    assert result["available_seats"] == 2
    assert result["requested_passengers"] == 3


def test_confirm_booking_endpoint_decrements_seats(client, db_session):
    """Test explicit HITL confirmation decrements seats in flight inventory."""
    flight_before = db_session.query(FlightModel).filter(FlightModel.id == "flight-del-bom-1").first()
    initial_seats = flight_before.available_seats

    # 1. Create Pending Booking
    create_payload = {
        "flight_id": "flight-del-bom-1",
        "contact_email": "traveler@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {"first_name": "Kavita", "last_name": "Mehta", "age": 32, "gender": "Female"}
        ],
    }
    res = client.post("/api/v1/bookings", json=create_payload)
    assert res.status_code == 201
    booking_id = res.json()["id"]

    # Verify seats haven't decremented yet during PENDING
    db_session.refresh(flight_before)
    assert flight_before.available_seats == initial_seats

    # 2. Confirm booking via POST /bookings/{id}/confirm
    confirm_res = client.post(f"/api/v1/bookings/{booking_id}/confirm")
    assert confirm_res.status_code == 200
    confirm_data = confirm_res.json()
    assert confirm_data["status"] == "CONFIRMED"
    assert confirm_data["confirmed_at"] is not None

    # Verify seats atomically decremented
    db_session.refresh(flight_before)
    assert flight_before.available_seats == initial_seats - 1


def test_confirm_booking_by_pnr_reference(client, db_session):
    """Test confirming a booking using the PNR reference instead of UUID."""
    create_payload = {
        "flight_id": "flight-del-bom-2",
        "contact_email": "pnr.user@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {"first_name": "Arjun", "last_name": "Kapoor", "age": 35, "gender": "Male"}
        ],
    }
    res = client.post("/api/v1/bookings", json=create_payload)
    assert res.status_code == 201
    pnr = res.json()["booking_reference"]

    # Confirm using PNR
    confirm_res = client.post(f"/api/v1/bookings/{pnr}/confirm")
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "CONFIRMED"
    assert confirm_res.json()["booking_reference"] == pnr


def test_cancel_booking_releases_seats(client, db_session):
    """Test cancellation of confirmed booking releases inventory back to flight."""
    flight = db_session.query(FlightModel).filter(FlightModel.id == "flight-del-bom-2").first()
    initial_seats = flight.available_seats

    # 1. Create and confirm
    create_payload = {
        "flight_id": "flight-del-bom-2",
        "contact_email": "cancel.user@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {"first_name": "Sunita", "last_name": "Rao", "age": 40, "gender": "Female"}
        ],
    }
    booking = client.post("/api/v1/bookings", json=create_payload).json()
    client.post(f"/api/v1/bookings/{booking['id']}/confirm")

    db_session.refresh(flight)
    assert flight.available_seats == initial_seats - 1

    # 2. Cancel booking
    cancel_res = client.post(f"/api/v1/bookings/{booking['id']}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Verify seats are restored
    db_session.refresh(flight)
    assert flight.available_seats == initial_seats


def test_cannot_confirm_cancelled_booking(client):
    """Test cancelled bookings cannot be subsequently confirmed."""
    create_payload = {
        "flight_id": "flight-del-bom-1",
        "contact_email": "test@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {"first_name": "Vijay", "last_name": "Nair", "age": 27, "gender": "Male"}
        ],
    }
    booking = client.post("/api/v1/bookings", json=create_payload).json()
    client.post(f"/api/v1/bookings/{booking['id']}/cancel")

    confirm_res = client.post(f"/api/v1/bookings/{booking['id']}/confirm")
    assert confirm_res.status_code == 400
    assert "cannot confirm a cancelled booking" in confirm_res.json()["detail"].lower()
