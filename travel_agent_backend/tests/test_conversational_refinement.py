"""Unit and integration tests for Phase 5 conversational search and state refinement."""

from typing import List, Dict, Any
from app.services.ranking_service import FlightRankingEngine
from app.agent.tools.comparison import compare_flights_tool
from app.agent.tools.registry import AVAILABLE_TOOLS, execute_tool
from app.agent.agent import AgentOrchestrator
from app.agent.state import TravelState
from app.llm.base import LLMInterface, LLMResponse, ToolCall, ChatMessage


def test_ranking_engine_scoring_and_badges():
    """Verify FlightRankingEngine calculates scores and assigns distinct badges."""
    sample_flights = [
        {
            "id": "f1",
            "flight_number": "AI-101",
            "airline": "Air India",
            "price": 6000.0,
            "duration_minutes": 120,
            "stops": 0,
        },
        {
            "id": "f2",
            "flight_number": "6E-202",
            "airline": "IndiGo",
            "price": 4000.0,
            "duration_minutes": 180,
            "stops": 1,
        },
        {
            "id": "f3",
            "flight_number": "QP-303",
            "airline": "Akasa Air",
            "price": 4500.0,
            "duration_minutes": 130,
            "stops": 0,
        },
    ]

    ranked = FlightRankingEngine.rank_flights(sample_flights)

    assert len(ranked) == 3
    # Check that each flight received a ranking_score and ranking_explanation
    for f in ranked:
        assert "ranking_score" in f
        assert "ranking_explanation" in f

    # Verify cheapest flight has Cheapest badge
    cheapest = next(f for f in ranked if f["flight_number"] == "6E-202")
    assert cheapest["badge"] == "Cheapest"

    # Verify fastest flight has Fastest badge or Best Overall
    fastest = next(f for f in ranked if f["flight_number"] == "AI-101")
    assert fastest["badge"] in ("Fastest", "Best Overall")

    # Verify best overall is first in list
    assert ranked[0]["badge"] in ("Best Overall", "Cheapest", "Fastest", "Non-stop")


def test_compare_flights_tool(db_session):
    """Verify compare_flights_tool computes price and time differentials between 2 flights."""
    args = {
        "flight_ids": ["flight-del-bom-1", "flight-del-bom-2"]
    }
    result = compare_flights_tool(db_session, args)

    assert result["status"] == "success"
    assert result["compared_count"] == 2
    assert "cheapest_flight" in result
    assert "fastest_flight" in result
    assert result["max_price_savings"] >= 0
    assert "summary" in result
    assert len(result["flights"]) == 2


def test_compare_flights_tool_insufficient_flights(db_session):
    """Verify compare_flights_tool returns error when fewer than 2 valid flights are found."""
    args = {
        "flight_ids": ["flight-del-bom-1", "non-existent-flight-id"]
    }
    result = compare_flights_tool(db_session, args)

    assert result["status"] == "error"
    assert "Could not find at least 2 flights" in result["message"]


def test_compare_flights_whitelist_registration():
    """Verify compare_flights is registered in AVAILABLE_TOOLS."""
    assert "compare_flights" in AVAILABLE_TOOLS


class MultiTurnMockLLM(LLMInterface):
    """Simulates multi-turn conversational tool execution and state refinement."""

    def __init__(self):
        self.turn = 0

    def generate_with_tools_sync(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        self.turn += 1

        # Turn 1: Search flights DEL to BOM
        if self.turn == 1:
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_t1",
                        name="search_flights",
                        arguments={"origin": "DEL", "destination": "BOM", "limit": 3},
                    )
                ],
                model="mock-llm",
            )
        elif self.turn == 2:
            return LLMResponse(
                content="Here are flights from Delhi to Mumbai.",
                tool_calls=[],
                model="mock-llm",
            )
        # Turn 3: Refine with non-stop only
        elif self.turn == 3:
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_t3",
                        name="filter_flights",
                        arguments={"origin": "DEL", "destination": "BOM", "max_stops": 0},
                    )
                ],
                model="mock-llm",
            )
        elif self.turn == 4:
            return LLMResponse(
                content="Here are the non-stop flights from Delhi to Mumbai.",
                tool_calls=[],
                model="mock-llm",
            )
        # Turn 5: Compare flights
        elif self.turn == 5:
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_t5",
                        name="compare_flights",
                        arguments={"flight_ids": ["flight-del-bom-1", "flight-del-bom-2"]},
                    )
                ],
                model="mock-llm",
            )
        return LLMResponse(
            content="Comparison complete: Flight 6E-204 is cheaper by ₹700.",
            tool_calls=[],
            model="mock-llm",
        )

    def generate_sync(self, messages, temperature=0.1, max_tokens=1000, json_mode=False):
        return LLMResponse(content="mock", model="mock-llm")

    async def generate(self, messages, temperature=0.1, max_tokens=1000, json_mode=False):
        return LLMResponse(content="mock", model="mock-llm")

    async def generate_with_tools(self, messages, tools, temperature=0.1):
        return self.generate_with_tools_sync(messages, tools, temperature)


def test_conversational_state_retention_and_refinement(db_session):
    """Verify state retention across multi-turn search -> filter refinement -> compare."""
    fake_llm = MultiTurnMockLLM()
    orchestrator = AgentOrchestrator(db=db_session, llm=fake_llm)

    # Turn 1: Search DEL to BOM
    state = TravelState()
    res1 = orchestrator.run("Find flights from Delhi to Mumbai", state=state)
    assert res1.state.origin == "DEL"
    assert res1.state.destination == "BOM"
    assert len(res1.recommended_flights) > 0
    assert len(res1.state.last_search_flight_ids) > 0

    # Turn 2: Refine: Only non-stop (origin and destination are preserved!)
    res2 = orchestrator.run("Only non-stop flights", state=res1.state)
    assert res2.state.origin == "DEL"
    assert res2.state.destination == "BOM"
    assert res2.state.max_stops == 0

    # Turn 3: Compare top 2 flights
    res3 = orchestrator.run("Compare top 2 flights", state=res2.state)
    assert res3.state.origin == "DEL"
    assert res3.state.destination == "BOM"
    assert len(res3.tool_trace) == 1
    assert res3.tool_trace[0].tool_name == "compare_flights"
    assert "Comparison complete" in res3.response
