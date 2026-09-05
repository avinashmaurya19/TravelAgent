"""Tests for Phase 8: Short-term conversation memory and user travel preferences."""

import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.models import UserModel
from app.database.repositories.conversation_repo import ConversationRepository
from app.database.repositories.preference_repo import UserPreferenceRepository
from app.services.ranking_service import FlightRankingEngine


def test_conversation_repository_lifecycle(db_session: Session):
    """Test creating session, appending messages, and retrieving history."""
    repo = ConversationRepository(db_session)
    session_id = f"sess-{uuid.uuid4()}"

    conv = repo.get_or_create_conversation(session_id)
    assert conv.session_id == session_id

    # Append user message
    msg1 = repo.append_message(session_id, role="user", content="Show flights to Goa")
    assert msg1.role == "user"
    assert msg1.content == "Show flights to Goa"

    # Append tool message
    msg2 = repo.append_message(
        session_id,
        role="tool",
        content='{"status": "success"}',
        tool_name="search_flights",
        tool_args={"origin": "DEL", "destination": "GOI"},
    )
    assert msg2.tool_name == "search_flights"

    # Append assistant message
    msg3 = repo.append_message(session_id, role="assistant", content="Found 3 flights.")
    assert msg3.role == "assistant"

    # Retrieve history
    history = repo.get_recent_messages(session_id)
    assert len(history) == 3
    assert history[0].role == "user"
    assert history[1].role == "tool"
    assert history[2].role == "assistant"


def test_user_preference_repository_lifecycle(db_session: Session):
    """Test user creation and preference upsert/retrieval."""
    repo = UserPreferenceRepository(db_session)
    email = f"traveler_{uuid.uuid4().hex[:6]}@example.com"

    user = repo.get_or_create_user(name="Rahul Sharma", email=email)
    assert user.name == "Rahul Sharma"
    assert user.email == email

    # Upsert preferences
    prefs = repo.set_preferences(
        user_id=user.id,
        preferred_cabin="business",
        preferred_airline="IndiGo",
        max_stops=0,
    )
    assert prefs.preferred_airline == "IndiGo"
    assert prefs.preferred_cabin == "business"
    assert prefs.max_stops == 0

    # Retrieve dict
    p_dict = repo.get_preferences_dict(user.id)
    assert p_dict["preferred_airline"] == "IndiGo"
    assert p_dict["max_stops"] == 0


def test_flight_ranking_with_preferred_airline():
    """Test that preferred airline gets a score discount and preferred badge."""
    sample_flights = [
        {
            "id": "f1",
            "flight_number": "AI-101",
            "airline": "Air India",
            "price": 5000.0,
            "duration_minutes": 130,
            "stops": 0,
        },
        {
            "id": "f2",
            "flight_number": "6E-202",
            "airline": "IndiGo",
            "price": 5100.0,
            "duration_minutes": 135,
            "stops": 0,
        },
    ]

    # Without preferences
    ranked_default = FlightRankingEngine.rank_flights(sample_flights)
    # With IndiGo preferred
    ranked_pref = FlightRankingEngine.rank_flights(
        sample_flights,
        user_preferences={"preferred_airline": "IndiGo", "max_stops": 0},
    )

    indigo_flight = next(f for f in ranked_pref if f["airline"] == "IndiGo")
    assert indigo_flight["is_preferred_airline"] is True
    assert "preferred airline" in indigo_flight["ranking_explanation"].lower()


def test_flight_ranking_explicit_query_override():
    """Guardrail: Explicit query for Air India must suppress background IndiGo preference."""
    sample_flights = [
        {
            "id": "f1",
            "flight_number": "AI-101",
            "airline": "Air India",
            "price": 5000.0,
            "duration_minutes": 120,
            "stops": 0,
        },
        {
            "id": "f2",
            "flight_number": "6E-202",
            "airline": "IndiGo",
            "price": 5050.0,
            "duration_minutes": 125,
            "stops": 0,
        },
    ]

    # User explicitly requested Air India in this turn
    ranked = FlightRankingEngine.rank_flights(
        sample_flights,
        user_preferences={"preferred_airline": "IndiGo"},
        explicit_query_airline="Air India",
    )

    indigo = next(f for f in ranked if f["airline"] == "IndiGo")
    assert indigo["is_preferred_airline"] is False
    assert ranked[0]["airline"] == "Air India"


def test_flight_ranking_with_max_stops_preference():
    """Test penalty when flight stops exceed user's preferred max_stops."""
    sample_flights = [
        {
            "id": "f1",
            "flight_number": "AI-101",
            "airline": "Air India",
            "price": 4000.0,
            "duration_minutes": 180,
            "stops": 1,
        },
        {
            "id": "f2",
            "flight_number": "6E-202",
            "airline": "IndiGo",
            "price": 4500.0,
            "duration_minutes": 120,
            "stops": 0,
        },
    ]

    ranked = FlightRankingEngine.rank_flights(
        sample_flights,
        user_preferences={"max_stops": 0},
    )

    assert ranked[0]["stops"] == 0


def test_users_api_endpoints(client: TestClient):
    """Test user profile creation and preference REST endpoints."""
    # Create user
    res = client.post(
        "/api/v1/users",
        json={"name": "Aman Verma", "email": f"aman_{uuid.uuid4().hex[:6]}@example.com"},
    )
    assert res.status_code == 201
    user_data = res.json()
    user_id = user_data["id"]

    # Get default preferences
    res_pref = client.get(f"/api/v1/users/{user_id}/preferences")
    assert res_pref.status_code == 200
    assert res_pref.json()["preferred_cabin"] == "economy"

    # Update preferences
    res_update = client.put(
        f"/api/v1/users/{user_id}/preferences",
        json={
            "preferred_cabin": "business",
            "preferred_airline": "Vistara",
            "max_stops": 0,
        },
    )
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["preferred_airline"] == "Vistara"
    assert updated["preferred_cabin"] == "business"


def test_chat_endpoint_persists_session_messages(client: TestClient, db_session: Session):
    """Test /agent/chat with session_id saves turns to the database."""
    session_id = f"test-sess-{uuid.uuid4()}"

    res = client.post(
        "/api/v1/agent/chat",
        json={
            "message": "Hi, how does this assistant work?",
            "session_id": session_id,
        },
    )
    assert res.status_code == 200

    # Verify messages saved to database
    repo = ConversationRepository(db_session)
    msgs = repo.get_recent_messages(session_id)
    assert len(msgs) >= 2  # user message and assistant message
    assert msgs[0].role == "user"
    assert msgs[-1].role == "assistant"
