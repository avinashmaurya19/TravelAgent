"""Core Agent Orchestrator implementing while-loop tool invocation and state tracking."""

import json
import time
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.llm.base import LLMInterface, ChatMessage
from app.llm.mistral import MistralLLM
from .state import TravelState
from .tools.registry import TOOL_SCHEMAS, execute_tool
from app.services.ranking_service import FlightRankingEngine

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """You are TravelAgent AI, an intelligent, helpful, and precise travel assistant.
You help users search for flights, filter results, inspect fare breakdowns, and initiate bookings across top Indian routes (DEL, BOM, BLR, GOI, CCU, HYD, MAA, PNQ, etc.).

Strict Operational Guidelines:
1. Tool-Gated Actions: NEVER make up or hallucinate flight schedules, flight numbers, or ticket fares. You MUST call deterministic tools ('search_flights', 'filter_flights', 'get_flight_details', 'compare_flights', 'check_availability', 'calculate_fare', 'create_booking', 'search_travel_policy') to query real inventory and policy clauses.
2. Informational & Guide Queries: If the user asks general questions (such as how the booking process works, how to use the assistant, travel guides, or greetings) without asking to search for flights between specific cities, answer helpfully in natural language text. DO NOT call 'search_flights' unless the user is actively requesting flight options.
3. Parameter Extraction: Extract 3-letter IATA airport codes (e.g. Delhi -> DEL, Mumbai -> BOM, Bangalore -> BLR, Goa -> GOI).
4. Conversational Refinement: Retain origin, destination, and dates across turns when users ask for "cheaper options", "only non-stop", "compare top flights", or "IndiGo flights".
5. Booking & Safe Confirmation (Human-in-the-Loop):
   - When the user asks to book (e.g. 'book this', 'please book', or provides passenger details like name, age, phone):
     a) Flight Selection: If user doesn't state a flight number, use the top/recommended flight from ActiveSearchResults (or previously discussed flight).
     b) Passenger Details: Extract first_name, last_name, age, gender, contact_phone, contact_email. Default email to 'guest@travelagent.ai' and phone to '9999999999' if omitted. DO NOT stop the booking process to ask for email if passenger name and age are provided.
     c) Tool Execution: Call 'create_booking' directly. DO NOT call 'compare_flights', 'check_availability', or 'calculate_fare' when the user has already requested to book!
     d) Human-in-the-Loop: Inform the user of their PNR reference and total fare, and instruct them that their pending booking requires explicit confirmation via the modal dialog. Never state that ticket issuance is finalized.
6. Comparison Tool Restriction: Call 'compare_flights' ONLY when the user explicitly requests to compare flight options (e.g. 'compare flights', 'what is the difference'). NEVER invoke 'compare_flights' when the user wants to book.
7. Grounded Travel Policy RAG: When the user asks about baggage limits, luggage allowances, ticket cancellations, refund amounts, or schedule delay compensation, you MUST call 'search_travel_policy'. Ground your response strictly in the retrieved policy text and cite the relevant section. NEVER hallucinate policy numbers or fees.
8. Format: Be concise, clear, and friendly. Quote prices in Indian Rupees (₹).
9. Open-Ended or Ambiguous Destinations: If the user requests flights to "anywhere", "somewhere", or leaves destination open without naming specific cities, DO NOT invoke more than 2 to 3 'search_flights' calls (e.g. query top popular destinations like BOM, BLR, or GOI only). Present those sample highlights and politely ask the user if they have a specific city or region in mind. NEVER query all destinations simultaneously.
"""


class ToolExecutionTrace(BaseModel):
    """Observability trace of an executed tool action."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    execution_time_ms: int


class AgentResult(BaseModel):
    """Final output from an agent reasoning and tool execution run."""
    response: str = Field(..., description="Assistant's natural language response")
    state: TravelState = Field(..., description="Updated conversation travel state")
    recommended_flights: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted flight recommendations")
    tool_trace: List[ToolExecutionTrace] = Field(default_factory=list, description="List of executed tool actions and timings")


class AgentOrchestrator:
    """Orchestrates multi-turn LLM reasoning, deterministic tool execution, and state persistence."""

    def __init__(
        self,
        db: Session,
        llm: Optional[LLMInterface] = None,
        max_iterations: int = 5,
        user_preferences: Optional[Dict[str, Any]] = None,
    ):
        self.db = db
        self.llm = llm or MistralLLM()
        self.max_iterations = max_iterations
        self.user_preferences = user_preferences

    def run(
        self,
        user_message: str,
        state: Optional[TravelState] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """Run the core while-loop agent orchestrator for a single user turn."""
        current_state = state or TravelState()
        tool_traces: List[ToolExecutionTrace] = []
        recommended_flights: List[Dict[str, Any]] = []
        current_preferences = user_preferences or self.user_preferences

        # Prepare messages with current date context
        from datetime import date as dt_date
        today_obj = dt_date.today()
        today_str = today_obj.strftime("%A, %B %d, %Y")
        system_content = (
            f"{AGENT_SYSTEM_PROMPT}\n\n"
            f"[Current Calendar Date]: Today is {today_str}. The current year is {today_obj.year}. "
            f"All travel dates refer to {today_obj.year} or future dates. NEVER search in past years like 2023 or 2024."
        )
        if current_preferences:
            pref_notes = []
            if current_preferences.get("preferred_airline"):
                pref_notes.append(f"Preferred Airline: {current_preferences['preferred_airline']}")
            if current_preferences.get("preferred_cabin"):
                pref_notes.append(f"Preferred Cabin: {current_preferences['preferred_cabin']}")
            if current_preferences.get("max_stops") is not None:
                pref_notes.append(f"Max Stops: {current_preferences['max_stops']}")
            if pref_notes:
                system_content += (
                    f"\n[User Travel Preferences]: {', '.join(pref_notes)}. "
                    "Respect these preferences by default unless the user explicitly requests something else in their query."
                )

        messages: List[ChatMessage] = [
            ChatMessage(role="system", content=system_content),
        ]

        # Inject existing state context if available
        if current_state.origin and current_state.destination:
            state_ctx = (
                f"[Current Travel Context]: Origin={current_state.origin}, "
                f"Destination={current_state.destination}, "
                f"Date={current_state.departure_date or 'Not specified'}, "
                f"Passengers={current_state.passengers}, "
                f"Budget={current_state.max_price or 'None'}, "
                f"Stops={current_state.max_stops if current_state.max_stops is not None else 'Any'}"
            )
            if current_state.last_search_flight_ids:
                state_ctx += f", ActiveSearchResults={current_state.last_search_flight_ids[:4]}"
            messages.append(ChatMessage(role="system", content=state_ctx))

        # Append prior chat history if present
        if chat_history:
            messages.extend(chat_history)

        # Append new user message
        messages.append(ChatMessage(role="user", content=user_message))

        iteration = 0
        final_text = ""

        while iteration < self.max_iterations:
            iteration += 1
            logger.info("Agent iteration %d/%d", iteration, self.max_iterations)

            # Generate model completion with registered tool whitelist
            response = self.llm.generate_with_tools_sync(
                messages=messages,
                tools=TOOL_SCHEMAS,
                temperature=0.1,
            )

            # Case A: Model requested tool invocations
            if response.tool_calls:
                # Add assistant message containing the tool calls
                formatted_tool_calls = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else str(tc.arguments),
                        },
                    }
                    for tc in response.tool_calls
                ]
                messages.append(
                    ChatMessage(
                        role="assistant",
                        content=response.content or "",
                        tool_calls=formatted_tool_calls,
                    )
                )

                for tc in response.tool_calls:
                    logger.info("Executing tool '%s' with args %s", tc.name, tc.arguments)
                    start_time = time.perf_counter()

                    # Execute deterministic tool with database session
                    tool_result = execute_tool(tc.name, tc.arguments, self.db)
                    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

                    # Update travel state from tool arguments and results
                    self._update_state(current_state, tc.name, tc.arguments, tool_result)

                    # Extract flight objects to return to UI cards and apply ranking
                    if "flights" in tool_result and isinstance(tool_result["flights"], list):
                        if tc.name in ("search_flights", "filter_flights"):
                            explicit_airline = (
                                tc.arguments.get("preferred_airline")
                                or current_state.preferred_airline
                            )
                            tool_result["flights"] = FlightRankingEngine.rank_flights(
                                tool_result["flights"],
                                user_preferences=current_preferences,
                                explicit_query_airline=explicit_airline,
                            )
                        recommended_flights = tool_result["flights"]
                    elif "flight" in tool_result and isinstance(tool_result["flight"], dict):
                        recommended_flights = [tool_result["flight"]]

                    # Record trace
                    trace = ToolExecutionTrace(
                        tool_name=tc.name,
                        arguments=tc.arguments,
                        result=tool_result,
                        execution_time_ms=elapsed_ms,
                    )
                    tool_traces.append(trace)

                    # Feed tool result back to LLM conversation
                    messages.append(
                        ChatMessage(
                            role="tool",
                            name=tc.name,
                            content=json.dumps(tool_result),
                            tool_call_id=tc.id,
                        )
                    )

                # Continue while loop to allow LLM to process tool results
                continue

            # Case B: Model returned natural language answer without tool calls
            final_text = response.content or "I have processed your request."
            break

        if not final_text and iteration >= self.max_iterations:
            final_text = "I completed searching our flight inventory. Please see the recommendations above."

        return AgentResult(
            response=final_text,
            state=current_state,
            recommended_flights=recommended_flights,
            tool_trace=tool_traces,
        )

    def _update_state(
        self,
        state: TravelState,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
    ) -> None:
        """Update active TravelState from tool inputs and execution results."""
        if tool_name in ("search_flights", "filter_flights"):
            if "origin" in arguments:
                state.origin = arguments["origin"].upper()
            if "destination" in arguments:
                state.destination = arguments["destination"].upper()
            if "departure_date" in arguments:
                state.departure_date = arguments["departure_date"]
            if "passengers" in arguments:
                state.passengers = arguments["passengers"]
            if "cabin_class" in arguments:
                state.cabin_class = arguments["cabin_class"]
            if "max_price" in arguments:
                state.max_price = arguments["max_price"]
            if "max_stops" in arguments:
                state.max_stops = arguments["max_stops"]
            if "preferred_airline" in arguments:
                state.preferred_airline = arguments["preferred_airline"]

            if result.get("status") == "success" and "flights" in result:
                state.last_search_flight_ids = [f["id"] for f in result["flights"] if "id" in f]

        elif tool_name == "create_booking":
            if result.get("status") == "pending_confirmation":
                state.booking_id = result.get("booking_id")
                state.booking_reference = result.get("booking_reference")
                if "flight" in result and isinstance(result["flight"], dict):
                    state.selected_flight_id = result["flight"].get("id")

        elif tool_name == "compare_flights":
            if result.get("status") == "success" and "flights" in result:
                state.last_search_flight_ids = [f["id"] for f in result["flights"] if "id" in f]
