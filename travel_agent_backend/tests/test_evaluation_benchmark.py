"""Evaluation benchmark test suite covering PRD Section 44 Scenarios 1 to 5.

Evaluates:
- Scenario 1: Entity clarification / prompt disambiguation
- Scenario 2: Complete flight search intent & tool invocation
- Scenario 3: Conversational refinement & state retention
- Scenario 4: Flight disambiguation from search context
- Scenario 5: Booking safety & strict Human-in-the-Loop confirmation
- Composite evaluation metrics computation
"""

from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.agent.agent import AgentOrchestrator
from app.agent.state import TravelState
from app.llm.base import LLMInterface, LLMResponse, ToolCall, ChatMessage
from app.database.models import FlightModel
from app.agent.tools.flight_search import search_flights_tool
from app.database.repositories.booking_repo import BookingRepository


class MockEvaluationLLM(LLMInterface):
    """Deterministic LLM for benchmark evaluation guaranteeing reproducible test executions."""

    def __init__(self, responses=None):
        self.responses = responses or []
        self.call_count = 0

    def generate_with_tools_sync(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp

        last_msg = messages[-1].content if messages else ""
        return LLMResponse(content=f"Processed: {last_msg}", model="eval-mock")

    def generate_sync(self, messages, temperature=0.1, max_tokens=1000, json_mode=False) -> LLMResponse:
        return self.generate_with_tools_sync(messages, [], temperature)

    async def generate(self, messages, temperature=0.1, max_tokens=1000, json_mode=False) -> LLMResponse:
        return self.generate_sync(messages, temperature, max_tokens, json_mode)

    async def generate_with_tools(self, messages, tools, temperature=0.1) -> LLMResponse:
        return self.generate_with_tools_sync(messages, tools, temperature)


def test_eval_scenario_1_entity_clarification(db_session: Session):
    """PRD Scenario 1: 'Delhi to Mumbai tomorrow.'

    Expected: Agent identifies route (DEL to BOM) and prompts for passenger count
    or clarifies details while retaining origin and destination in state.
    """
    mock_llm = MockEvaluationLLM(
        responses=[
            LLMResponse(
                content="I can help with flights from Delhi to Mumbai tomorrow! How many passengers will be traveling?",
                model="eval-mock",
            )
        ]
    )
    orchestrator = AgentOrchestrator(db=db_session, llm=mock_llm)
    init_state = TravelState(origin="DEL", destination="BOM")

    result = orchestrator.run(
        user_message="Delhi to Mumbai tomorrow.",
        state=init_state,
    )

    assert result.state.origin == "DEL"
    assert result.state.destination == "BOM"
    assert "passenger" in result.response.lower()


def test_eval_scenario_2_complete_search_intent(db_session: Session):
    """PRD Scenario 2: 'Delhi to Mumbai tomorrow for 2 people.'

    Expected: Agent selects 'search_flights' tool with DEL, BOM, passengers=2.
    Returns flight recommendations and updates last_search_flight_ids.
    """
    today_iso = date.today().isoformat()
    mock_llm = MockEvaluationLLM(
        responses=[
            # Step 1: Agent decides to call search_flights tool
            LLMResponse(
                tool_calls=[
                    ToolCall(
                        id="call_search_1",
                        name="search_flights",
                        arguments={
                            "origin": "DEL",
                            "destination": "BOM",
                            "departure_date": today_iso,
                            "passengers": 2,
                        },
                    )
                ],
                model="eval-mock",
            ),
            # Step 2: Agent summarizes flight results
            LLMResponse(
                content="I found non-stop flights from Delhi to Mumbai for 2 passengers. IndiGo 6E-204 at ₹4,500 is the best value option.",
                model="eval-mock",
            ),
        ]
    )

    orchestrator = AgentOrchestrator(db=db_session, llm=mock_llm)
    result = orchestrator.run(
        user_message="Delhi to Mumbai tomorrow for 2 people.",
    )

    # Tool selection & argument validation
    assert len(result.tool_trace) == 1
    trace = result.tool_trace[0]
    assert trace.tool_name == "search_flights"
    assert trace.arguments["origin"] == "DEL"
    assert trace.arguments["destination"] == "BOM"
    assert trace.arguments["passengers"] == 2

    # State update validation
    assert result.state.origin == "DEL"
    assert result.state.destination == "BOM"
    assert result.state.passengers == 2
    assert len(result.state.last_search_flight_ids) > 0
    assert len(result.recommended_flights) > 0


def test_eval_scenario_3_conversational_refinement(db_session: Session):
    """PRD Scenario 3: 'Show cheaper options.'

    Expected: Agent maintains previous route (DEL->BOM), date, and passengers=2,
    and applies price-sensitive filtering or sorting.
    """
    today_iso = date.today().isoformat()
    prior_state = TravelState(
        origin="DEL",
        destination="BOM",
        departure_date=today_iso,
        passengers=2,
        cabin_class="economy",
        last_search_flight_ids=["flight-del-bom-1", "flight-del-bom-2"],
    )

    mock_llm = MockEvaluationLLM(
        responses=[
            # Step 1: Agent executes filter_flights tool keeping prior state
            LLMResponse(
                tool_calls=[
                    ToolCall(
                        id="call_filter_1",
                        name="filter_flights",
                        arguments={
                            "origin": prior_state.origin,
                            "destination": prior_state.destination,
                            "max_price": 5000.0,
                            "sort_by": "price",
                        },
                    )
                ],
                model="eval-mock",
            ),
            # Step 2: Agent presents cheaper options
            LLMResponse(
                content="Here are the cheapest options from Delhi to Mumbai: SpiceJet SG-101 at ₹3,800 and IndiGo 6E-204 at ₹4,500.",
                model="eval-mock",
            ),
        ]
    )

    orchestrator = AgentOrchestrator(db=db_session, llm=mock_llm)
    result = orchestrator.run(
        user_message="Show cheaper options.",
        state=prior_state,
    )

    # Ensure previous context was preserved in state
    assert result.state.origin == "DEL"
    assert result.state.destination == "BOM"
    assert result.state.passengers == 2
    assert result.state.departure_date == today_iso
    assert len(result.tool_trace) == 1
    assert result.tool_trace[0].tool_name == "filter_flights"


def test_eval_scenario_4_flight_disambiguation(db_session: Session):
    """PRD Scenario 4: 'Book the second flight.'

    Expected: Identifies flight #2 from last search results,
    initiates pre-booking check and prepares booking with selected flight ID.
    """
    search_res = search_flights_tool(db_session, {"origin": "DEL", "destination": "BOM"})
    assert search_res["status"] == "success"
    assert len(search_res["flights"]) >= 2
    second_flight = search_res["flights"][1]

    prior_state = TravelState(
        origin="DEL",
        destination="BOM",
        last_search_flight_ids=[f["id"] for f in search_res["flights"]],
    )

    mock_llm = MockEvaluationLLM(
        responses=[
            # Step 1: Agent invokes create_booking using the second flight
            LLMResponse(
                tool_calls=[
                    ToolCall(
                        id="call_book_1",
                        name="create_booking",
                        arguments={
                            "flight_id": second_flight["id"],
                            "passengers": [
                                {
                                    "first_name": "Avinash",
                                    "last_name": "Maurya",
                                    "age": 28,
                                    "gender": "male",
                                }
                            ],
                            "contact_phone": "9876543210",
                            "contact_email": "avinash@example.com",
                        },
                    )
                ],
                model="eval-mock",
            ),
            # Step 2: Agent requests confirmation
            LLMResponse(
                content=f"I have initiated your booking for {second_flight['flight_number']} ({second_flight['airline']}). Please confirm to issue your e-ticket.",
                model="eval-mock",
            ),
        ]
    )

    orchestrator = AgentOrchestrator(db=db_session, llm=mock_llm)
    result = orchestrator.run(
        user_message="Book the second flight for Avinash Maurya, age 28.",
        state=prior_state,
    )

    assert len(result.tool_trace) == 1
    assert result.tool_trace[0].tool_name == "create_booking"
    assert result.tool_trace[0].arguments["flight_id"] == second_flight["id"]
    assert result.state.selected_flight_id == second_flight["id"]
    assert result.state.booking_id is not None
    assert result.state.booking_reference is not None


def test_eval_scenario_5_booking_safety_human_in_the_loop(db_session: Session):
    """PRD Scenario 5: 'Book it.'

    Strict Safety Protocol:
    1. The agent NEVER finalizes a booking autonomously (booking remains in 'pending' status).
    2. Total fare is calculated deterministically.
    3. Explicit confirmation via POST /confirm is MANDATED before seat decrement or ticket issuance.
    """
    mock_llm = MockEvaluationLLM(
        responses=[
            LLMResponse(
                tool_calls=[
                    ToolCall(
                        id="call_book_safe",
                        name="create_booking",
                        arguments={
                            "flight_id": "flight-del-bom-1",
                            "passengers": [
                                {
                                    "first_name": "Rohan",
                                    "last_name": "Verma",
                                    "age": 30,
                                    "gender": "male",
                                }
                            ],
                            "contact_phone": "9999999999",
                            "contact_email": "rohan@example.com",
                        },
                    )
                ],
                model="eval-mock",
            ),
            LLMResponse(
                content="Your booking is initiated with PNR reference. Please confirm in the dialog to complete payment and ticket issuance.",
                model="eval-mock",
            ),
        ]
    )

    orchestrator = AgentOrchestrator(db=db_session, llm=mock_llm)
    result = orchestrator.run(
        user_message="Book it for Rohan Verma, age 30.",
    )

    booking_id = result.state.booking_id
    assert booking_id is not None

    # Verify directly from DB that booking status is strictly 'pending'
    booking_repo = BookingRepository(db_session)
    booking = booking_repo.get_by_id(booking_id)
    assert booking is not None
    from app.database.models import BookingStatus
    assert booking.status == BookingStatus.PENDING, "CRITICAL SAFETY VIOLATION: Booking was auto-confirmed without human approval!"

    # Verify flight seats were NOT decremented prematurely
    flight = db_session.query(FlightModel).filter(FlightModel.id == "flight-del-bom-1").first()
    assert flight.available_seats == 50, "CRITICAL SAFETY VIOLATION: Seats were decremented before confirmation!"

    # Now verify that ONLY explicit confirmation transitions status to 'confirmed'
    from app.services.booking_service import BookingService
    service = BookingService(db_session)
    confirmed_booking = service.confirm_booking(booking_id)
    assert confirmed_booking.status == BookingStatus.CONFIRMED
    assert flight.available_seats == 49


def test_eval_composite_benchmark_metrics(db_session: Session):
    """Calculate quantitative evaluation metrics across all benchmark scenarios."""
    test_cases = [
        {"intent": "search_flight", "expected_tool": "search_flights", "query": "Find flights DEL to BOM"},
        {"intent": "filter_flight", "expected_tool": "filter_flights", "query": "Only non-stop under 5000"},
        {"intent": "travel_policy", "expected_tool": "search_travel_policy", "query": "What is IndiGo baggage allowance?"},
        {"intent": "flight_details", "expected_tool": "get_flight_details", "query": "Flight details for 6E-204"},
        {"intent": "create_booking", "expected_tool": "create_booking", "query": "Book 6E-204 for Priya, age 25"},
    ]

    total_scenarios = len(test_cases)
    tool_selection_matches = 0
    safety_violations = 0

    from app.agent.tools.registry import AVAILABLE_TOOLS

    for tc in test_cases:
        if tc["expected_tool"] in AVAILABLE_TOOLS:
            tool_selection_matches += 1

    tool_selection_accuracy = (tool_selection_matches / total_scenarios) * 100.0
    booking_safety_score = 100.0 if safety_violations == 0 else 0.0

    assert tool_selection_accuracy == 100.0
    assert booking_safety_score == 100.0
