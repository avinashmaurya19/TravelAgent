"""Unit and integration tests for Phase 9: Real-time SSE streaming and observability."""

import uuid
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.agent.agent import AgentOrchestrator
from app.agent.state import TravelState
from app.database.repositories.conversation_repo import ConversationRepository


def test_agent_run_stream_yields_events(db_session: Session):
    """Test that run_stream yields start, assistant_message, and stream_end for general query."""
    orchestrator = AgentOrchestrator(db=db_session)
    events = list(orchestrator.run_stream(user_message="Hello, what can you do?"))

    event_types = [e["event"] for e in events]
    assert "start" in event_types
    assert "assistant_message" in event_types
    assert "stream_end" in event_types

    # Verify assistant_message contains response and state
    msg_event = next(e for e in events if e["event"] == "assistant_message")
    assert "response" in msg_event["data"]
    assert "state" in msg_event["data"]


def test_agent_run_stream_yields_tool_events(db_session: Session):
    """Test that run_stream yields tool_start and tool_result when tools are executed."""
    orchestrator = AgentOrchestrator(db=db_session)
    events = list(
        orchestrator.run_stream(
            user_message="Find flights from DEL to BOM tomorrow",
            state=TravelState(origin="DEL", destination="BOM"),
        )
    )

    event_types = [e["event"] for e in events]
    assert "start" in event_types
    assert "tool_start" in event_types
    assert "tool_result" in event_types
    assert "assistant_message" in event_types
    assert "stream_end" in event_types

    tool_start = next(e for e in events if e["event"] == "tool_start")
    assert "tool_name" in tool_start["data"]
    assert "arguments" in tool_start["data"]

    tool_result = next(e for e in events if e["event"] == "tool_result")
    assert "result" in tool_result["data"]
    assert "execution_time_ms" in tool_result["data"]


def test_chat_stream_api_endpoint(client: TestClient):
    """Test POST /api/v1/agent/chat/stream returns valid SSE stream."""
    session_id = f"stream-sess-{uuid.uuid4()}"

    res = client.post(
        "/api/v1/agent/chat/stream",
        json={
            "message": "Hello, how does this assistant work?",
            "session_id": session_id,
        },
    )
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]

    # Parse SSE events from response text
    body = res.text
    assert "event: start" in body
    assert "event: assistant_message" in body
    assert "event: stream_end" in body


def test_chat_stream_persists_session_in_db(client: TestClient, db_session: Session):
    """Test that streaming endpoint persists conversation turns in the database."""
    session_id = f"stream-db-{uuid.uuid4()}"

    res = client.post(
        "/api/v1/agent/chat/stream",
        json={
            "message": "Hi, what are the baggage limits?",
            "session_id": session_id,
        },
    )
    assert res.status_code == 200

    repo = ConversationRepository(db_session)
    messages = repo.get_recent_messages(session_id)
    assert len(messages) >= 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hi, what are the baggage limits?"
    assert messages[-1].role == "assistant"
