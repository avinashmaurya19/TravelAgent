"""Unit & integration tests for Flight endpoints and services."""

from datetime import date


def test_search_flights_basic(client):
    """Test standard flight search between origin and destination."""
    today_str = date.today().isoformat()
    response = client.get(f"/api/v1/flights/search?origin=DEL&destination=BOM&departure_date={today_str}&passengers=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    for flight in data:
        assert flight["origin"] == "DEL"
        assert flight["destination"] == "BOM"


def test_search_flights_filter_max_price(client):
    """Test filtering flights by budget max_price."""
    today_str = date.today().isoformat()
    response = client.get(
        f"/api/v1/flights/search?origin=DEL&destination=BOM&departure_date={today_str}&max_price=4600"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for flight in data:
        assert flight["price"] <= 4600.0


def test_search_flights_filter_airline(client):
    """Test filtering flights by preferred airline."""
    today_str = date.today().isoformat()
    response = client.get(
        f"/api/v1/flights/search?origin=DEL&destination=BOM&departure_date={today_str}&preferred_airline=IndiGo"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["airline"] == "IndiGo"


def test_search_flights_cabin_class(client):
    """Test filtering business class flights."""
    today_str = date.today().isoformat()
    response = client.get(
        f"/api/v1/flights/search?origin=DEL&destination=BOM&departure_date={today_str}&cabin_class=business"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cabin_class"] == "business"


def test_get_flight_details_success(client):
    """Test retrieving existing flight by UUID."""
    response = client.get("/api/v1/flights/flight-del-bom-1")
    assert response.status_code == 200
    data = response.json()
    assert data["flight_number"] == "6E-204"
    assert data["origin"] == "DEL"
    assert data["destination"] == "BOM"


def test_get_flight_details_not_found(client):
    """Test 404 response on invalid flight ID."""
    response = client.get("/api/v1/flights/non-existent-uuid")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_check_availability(client):
    """Test seat availability endpoint."""
    # Available seats = 2 for lowseats flight
    resp_avail = client.get("/api/v1/flights/flight-del-bom-lowseats/availability?passengers=2")
    assert resp_avail.status_code == 200
    assert resp_avail.json()["is_available"] is True

    # Requesting 3 should return is_available: False
    resp_unavail = client.get("/api/v1/flights/flight-del-bom-lowseats/availability?passengers=3")
    assert resp_unavail.status_code == 200
    assert resp_unavail.json()["is_available"] is False


def test_calculate_fare_breakdown(client):
    """Test deterministic fare calculation with tax and extra baggage."""
    payload = {
        "flight_id": "flight-del-bom-1",
        "passengers_count": 2,
        "add_extra_baggage": True,
        "seat_selection": "extra_legroom",
    }
    response = client.post("/api/v1/flights/fare-breakdown", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Base price = 4500 * 2 = 9000
    assert data["base_fare_per_passenger"] == 4500.0
    assert data["total_base_fare"] == 9000.0
    # Tax = 9000 * 0.18 = 1620.0
    assert data["tax_amount"] == 1620.0
    # Baggage = 1200 * 2 = 2400.0
    assert data["baggage_fee"] == 2400.0
    # Seat = 600 * 2 = 1200.0
    assert data["seat_fee"] == 1200.0
    # Total = 9000 + 1620 + 2400 + 1200 = 14220.0
    assert data["total_amount"] == 14220.0


def test_lookup_by_flight_number(client):
    """Test that flight details and fare breakdown also work when passing flight_number (e.g. 6E-204)."""
    # Test details lookup by flight number
    response = client.get("/api/v1/flights/6E-204")
    assert response.status_code == 200
    assert response.json()["flight_number"] == "6E-204"

    # Test fare breakdown by flight number
    payload = {
        "flight_id": "6E-204",
        "passengers_count": 1,
        "add_extra_baggage": False,
        "seat_selection": "standard",
    }
    fare_resp = client.post("/api/v1/flights/fare-breakdown", json=payload)
    assert fare_resp.status_code == 200
    assert fare_resp.json()["flight_number"] == "6E-204"

