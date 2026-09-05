"""Integration tests for AgentOrchestrator loop and POST /agent/chat."""

from typing import List, Dict, Any
from app.llm.base import LLMInterface, LLMResponse, ToolCall, ChatMessage
from app.agent.agent import AgentOrchestrator
from app.agent.state import TravelState


class FakeToolCallingLLM(LLMInterface):
    """Fake LLM that simulates emitting a tool call on turn 1, then answering on turn 2."""

    def __init__(self):
        self.call_count = 0

    def generate_with_tools_sync(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        self.call_count += 1
        if self.call_count == 1:
            # Emit search_flights tool call
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_mock_1",
                        name="search_flights",
                        arguments={"origin": "DEL", "destination": "BOM", "limit": 3},
                    )
                ],
                model="fake-llm",
            )
        # Turn 2: Synthesize final response
        return LLMResponse(
            content="I found 3 great flights from Delhi to Mumbai. Let me know which one you prefer!",
            tool_calls=[],
            model="fake-llm",
        )

    def generate_sync(self, messages, temperature=0.1, max_tokens=1000, json_mode=False):
        return LLMResponse(content="Fake response", model="fake-llm")

    async def generate(self, messages, temperature=0.1, max_tokens=1000, json_mode=False):
        return LLMResponse(content="Fake response", model="fake-llm")

    async def generate_with_tools(self, messages, tools, temperature=0.1):
        return self.generate_with_tools_sync(messages, tools, temperature)


def test_agent_orchestrator_tool_loop(db_session):
    """Verify orchestrator runs tool loop, updates state, and returns recommended flights."""
    fake_llm = FakeToolCallingLLM()
    orchestrator = AgentOrchestrator(db=db_session, llm=fake_llm)

    state = TravelState()
    result = orchestrator.run("Find flights from Delhi to Mumbai", state=state)

    assert result.response != ""
    assert len(result.tool_trace) == 1
    assert result.tool_trace[0].tool_name == "search_flights"
    assert result.state.origin == "DEL"
    assert result.state.destination == "BOM"
    assert len(result.recommended_flights) > 0


def test_api_agent_chat_endpoint(client):
    """Verify POST /api/v1/agent/chat executes orchestrator and returns 200."""
    payload = {
        "message": "Find flights from Delhi to Mumbai tomorrow under 6000",
        "state": {
            "origin": "DEL",
            "destination": "BOM",
        },
    }
    response = client.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "state" in data
    assert "tool_trace" in data
    assert data["state"]["origin"] == "DEL"
