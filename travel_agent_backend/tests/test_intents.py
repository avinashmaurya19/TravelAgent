"""Unit tests for IntentEngine and POST /agent/intent endpoint."""

import pytest
from app.agent.intents import IntentType
from app.agent.intent_engine import IntentEngine


def test_intent_search_flight_with_budget():
    """Verify intent recognition extracts route and price cap."""
    engine = IntentEngine()
    intent = engine.recognize_intent_sync("I want to fly from Delhi to Mumbai tomorrow under 5000")
    assert intent.intent == IntentType.SEARCH_FLIGHT
    assert intent.origin == "DEL"
    assert intent.destination == "BOM"
    assert intent.max_price == 5000.0


def test_intent_nonstop_airline_filter():
    """Verify non-stop constraint and preferred airline recognition."""
    engine = IntentEngine()
    intent = engine.recognize_intent_sync("Direct IndiGo flight from Bangalore to Delhi")
    assert intent.intent == IntentType.SEARCH_FLIGHT
    assert intent.origin == "BLR"
    assert intent.destination == "DEL"
    assert intent.max_stops == 0
    assert intent.preferred_airline == "IndiGo"


def test_intent_travel_policy():
    """Verify policy topic recognition."""
    engine = IntentEngine()
    intent = engine.recognize_intent_sync("What is the baggage limit for domestic flights?")
    assert intent.intent == IntentType.TRAVEL_POLICY
    assert intent.policy_topic == "baggage"


def test_intent_check_booking_pnr():
    """Verify PNR reference extraction."""
    engine = IntentEngine()
    intent = engine.recognize_intent_sync("Check status for booking DELBOM99")
    assert intent.intent == IntentType.CHECK_BOOKING
    assert intent.booking_reference == "DELBOM99"


def test_intent_compare_flights():
    """Verify flight comparison intent."""
    engine = IntentEngine()
    intent = engine.recognize_intent_sync("Compare the first 2 flights")
    assert intent.intent == IntentType.COMPARE_FLIGHTS


def test_intent_cancel_booking():
    """Verify booking cancellation intent."""
    engine = IntentEngine()
    intent = engine.recognize_intent_sync("Please cancel my booking")
    assert intent.intent == IntentType.CANCEL_BOOKING


def test_api_agent_intent_endpoint(client):
    """Verify POST /api/v1/agent/intent returns 200 and valid AgentIntent schema."""
    payload = {"query": "Find cheapest flight from Delhi to Goa this weekend under 7000"}
    response = client.post("/api/v1/agent/intent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "SEARCH_FLIGHT"
    assert data["origin"] == "DEL"
    assert data["destination"] == "GOI"
    assert data["max_price"] == 7000.0
