"""Unit tests for deterministic agent tools and security whitelist."""

from app.agent.tools.registry import AVAILABLE_TOOLS, execute_tool
from app.agent.tools.flight_search import search_flights_tool
from app.agent.tools.flight_details import get_flight_details_tool
from app.agent.tools.filtering import filter_flights_tool
from app.agent.tools.availability import check_availability_tool
from app.agent.tools.fare import calculate_fare_tool
from app.agent.tools.booking import create_booking_tool


def test_tool_whitelist_contents():
    """Verify all 6 core deterministic tools are registered in whitelist."""
    expected_tools = {
        "search_flights",
        "get_flight_details",
        "filter_flights",
        "check_availability",
        "calculate_fare",
        "create_booking",
    }
    assert expected_tools.issubset(set(AVAILABLE_TOOLS.keys()))


def test_execute_tool_unauthorized_rejection(db_session):
    """Verify executing an unauthorized tool is blocked by security guardrails."""
    res = execute_tool("execute_raw_sql", {"query": "DROP TABLE flights;"}, db_session)
    assert res["status"] == "error"
    assert res["error_type"] == "SecurityViolation"
    assert "whitelist" in res["message"]


def test_search_flights_tool(db_session):
    """Verify search_flights tool queries inventory and returns flights."""
    args = {"origin": "DEL", "destination": "BOM", "limit": 5}
    res = search_flights_tool(db_session, args)
    assert res["status"] == "success"
    assert res["origin"] == "DEL"
    assert res["destination"] == "BOM"
    assert len(res["flights"]) > 0


def test_flight_details_tool(db_session):
    """Verify get_flight_details tool retrieves flight by ID."""
    res = get_flight_details_tool(db_session, {"flight_id": "flight-del-bom-1"})
    assert res["status"] == "success"
    assert res["flight"]["flight_number"] == "6E-204"


def test_flight_details_tool_not_found(db_session):
    """Verify get_flight_details tool returns not_found on unknown ID."""
    res = get_flight_details_tool(db_session, {"flight_id": "nonexistent-id"})
    assert res["status"] == "not_found"


def test_filter_flights_tool(db_session):
    """Verify filter_flights tool applies max_price and stops filters."""
    args = {
        "origin": "DEL",
        "destination": "BOM",
        "max_price": 5000.0,
        "max_stops": 0,
    }
    res = filter_flights_tool(db_session, args)
    assert res["status"] == "success"
    for f in res["flights"]:
        assert f["price"] <= 5000.0
        assert f["stops"] == 0


def test_check_availability_tool(db_session):
    """Verify check_availability tool reports seat availability."""
    res = check_availability_tool(db_session, {"flight_id": "flight-del-bom-1", "passengers": 2})
    assert res["status"] == "success"
    assert res["is_available"] is True


def test_calculate_fare_tool(db_session):
    """Verify calculate_fare tool calculates base fare, GST, and extras."""
    args = {
        "flight_id": "flight-del-bom-1",
        "passengers": 2,
        "add_extra_baggage": True,
        "seat_selection": "extra_legroom",
    }
    res = calculate_fare_tool(db_session, args)
    assert res["status"] == "success"
    breakdown = res["fare_breakdown"]
    assert breakdown["passengers_count"] == 2
    assert breakdown["tax_amount"] > 0
    assert breakdown["baggage_fee"] > 0
    assert breakdown["total_amount"] > breakdown["total_base_fare"]


def test_create_booking_tool_pending_state(db_session):
    """Verify create_booking tool generates a PENDING reservation requiring confirmation."""
    args = {
        "flight_id": "flight-del-bom-1",
        "passengers": [
            {
                "first_name": "Aarav",
                "last_name": "Patel",
                "age": 29,
                "gender": "Male",
            }
        ],
        "contact_email": "aarav.patel@example.com",
    }
    res = create_booking_tool(db_session, args)
    assert res["status"] == "pending_confirmation"
    assert res["human_confirmation_required"] is True
    assert "booking_reference" in res
    assert res["total_price"] > 0
