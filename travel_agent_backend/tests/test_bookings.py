"""Unit & integration tests for Booking endpoints and lifecycle."""

def test_create_pending_booking_success(client):
    """Test creating a booking in PENDING state with passenger list."""
    payload = {
        "flight_id": "flight-del-bom-1",
        "contact_email": "passenger@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {
                "first_name": "Rahul",
                "last_name": "Sharma",
                "age": 30,
                "gender": "Male",
                "seat_number": "14A",
            }
        ],
        "add_extra_baggage": False,
        "seat_selection_tier": "standard",
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "PENDING"
    assert data["booking_reference"].startswith("TA")
    assert data["passengers_count"] == 1
    assert data["total_price"] == 5310.0  # 4500 base + 810 GST
    assert len(data["passengers"]) == 1
    assert data["passengers"][0]["first_name"] == "Rahul"


def test_create_booking_insufficient_seats(client):
    """Test booking creation failure when requested seats exceed availability."""
    payload = {
        "flight_id": "flight-del-bom-lowseats",  # Has only 2 seats
        "contact_email": "group@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {"first_name": "P1", "last_name": "L1", "age": 25, "gender": "Male"},
            {"first_name": "P2", "last_name": "L2", "age": 26, "gender": "Female"},
            {"first_name": "P3", "last_name": "L3", "age": 27, "gender": "Male"},
        ],
    }
    response = client.post("/api/v1/bookings", json=payload)
    assert response.status_code == 400
    assert "insufficient seats" in response.json()["detail"].lower()


def test_confirm_booking_lifecycle(client):
    """Test full booking lifecycle: Create PENDING -> Confirm -> Status CONFIRMED."""
    # 1. Create Pending Booking
    create_payload = {
        "flight_id": "flight-del-bom-2",
        "contact_email": "traveler@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {"first_name": "Priya", "last_name": "Verma", "age": 28, "gender": "Female"}
        ],
    }
    create_resp = client.post("/api/v1/bookings", json=create_payload)
    assert create_resp.status_code == 201
    booking_id = create_resp.json()["id"]

    # 2. Check initial seats count (flight-del-bom-2 had 20 seats)
    flight_resp = client.get("/api/v1/flights/flight-del-bom-2")
    assert flight_resp.json()["available_seats"] == 20

    # 3. Explicitly Confirm Booking (Human-in-the-loop)
    confirm_resp = client.post(f"/api/v1/bookings/{booking_id}/confirm", json={"payment_method": "UPI"})
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "CONFIRMED"
    assert confirm_resp.json()["confirmed_at"] is not None

    # 4. Verify seat inventory was decremented (20 - 1 = 19)
    flight_after_resp = client.get("/api/v1/flights/flight-del-bom-2")
    assert flight_after_resp.json()["available_seats"] == 19


def test_cancel_booking_workflow(client):
    """Test cancelling a confirmed booking restores flight seat count."""
    # 1. Create and confirm booking
    create_payload = {
        "flight_id": "flight-del-goi-1",  # Has 30 seats
        "contact_email": "cancel_test@example.com",
        "contact_phone": "9876543210",
        "passengers": [
            {"first_name": "Amit", "last_name": "Kapoor", "age": 35, "gender": "Male"}
        ],
    }
    create_resp = client.post("/api/v1/bookings", json=create_payload)
    booking_id = create_resp.json()["id"]
    client.post(f"/api/v1/bookings/{booking_id}/confirm")

    # Verify seats became 29
    assert client.get("/api/v1/flights/flight-del-goi-1").json()["available_seats"] == 29

    # 2. Cancel booking
    cancel_resp = client.post(f"/api/v1/bookings/{booking_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"
    assert cancel_resp.json()["refund_amount"] > 0

    # 3. Verify seat inventory restored to 30
    assert client.get("/api/v1/flights/flight-del-goi-1").json()["available_seats"] == 30
