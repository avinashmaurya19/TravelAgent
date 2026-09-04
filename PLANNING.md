# 🗺️ TravelAgent AI — Architectural & Project Plan (`PLANNING.md`)

This document serves as the master planning blueprint for **TravelAgent AI**, viewed from three key perspectives: **Software Architect**, **Software Developer**, and **Product Manager**.

---

## 1. Multi-Angle Codebase & Architectural Overview

### 🏛️ Software Architect View
The system separates natural-language intelligence (LLM Agent) from business state and transactional logic (Deterministic Backend Services).

```text
                     ┌──────────────────────────┐
                     │   Flutter Mobile/Web     │
                     │  (Chat UI & Trace View)  │
                     └────────────┬─────────────┘
                                  │ REST / SSE
                     ┌────────────▼─────────────┐
                     │      FastAPI App         │
                     └────────────┬─────────────┘
                                  │
                     ┌────────────▼─────────────┐
                     │    Agent Orchestrator    │
                     └────────────┬─────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
             ┌──────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
             │    LLM     │ │  Tools    │ │ RAG/FAISS │
             │Mistral/HF  │ │ Repository│ │ Policy    │
             └────────────┘ └─────┬─────┘ └───────────┘
                                  │
                            ┌─────▼─────┐
                            │PostgreSQL │
                            │(Mock Data)│
                            └───────────┘
```

#### Core Design Decisions:
1. **Tool-Gated LLM**: The LLM never touches the database directly. All inventory searches, availability checks, fare calculations, and bookings pass through validated Pydantic tool functions.
2. **Pydantic State Persistence**: Conversation state is anchored in a `TravelState` structure (origin, destination, date, passengers, price limits, selected flight ID) rather than unstructured chat context alone.
3. **Dual-Check Booking Guardrail**: Booking requires a pre-flight re-check (`check_availability` + `calculate_fare`) and explicit human confirmation (`POST /confirm`).
4. **SSE Event Stream**: Real-time events (`tool_start`, `tool_result`, `thinking`, `assistant_message`) are pushed via SSE to drive dynamic UI widgets and live agent trace timelines.

---

### 💻 Software Developer View
The codebase is cleanly separated into backend (`travel_agent_backend`) and frontend (`travel_agent_flutter`).

#### Core Data Structures (Pydantic):
```python
# app/agent/state.py
from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, Any

class TravelState(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[date] = None
    passengers: int = 1
    cabin_class: str = "economy"
    max_price: Optional[float] = None
    max_stops: Optional[int] = None
    preferred_airline: Optional[str] = None
    selected_flight_id: Optional[str] = None
    passenger_details: Optional[Dict[str, Any]] = None
    booking_id: Optional[str] = None
```

```python
# app/agent/intents.py
from pydantic import BaseModel
from typing import Literal, Optional

class AgentIntent(BaseModel):
    intent: Literal[
        "SEARCH_FLIGHT",
        "REFINE_SEARCH",
        "FLIGHT_DETAILS",
        "COMPARE_FLIGHTS",
        "SELECT_FLIGHT",
        "BOOK_FLIGHT",
        "CHECK_BOOKING",
        "CANCEL_BOOKING",
        "TRAVEL_POLICY",
        "GENERAL_TRAVEL"
    ]
    origin: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[str] = None
    budget: Optional[float] = None
```

#### Tool Registry:
```python
AVAILABLE_TOOLS = {
    "search_flights": search_flights,
    "filter_flights": filter_flights,
    "get_flight_details": get_flight_details,
    "check_availability": check_availability,
    "calculate_fare": calculate_fare,
    "create_booking": create_booking,
    "cancel_booking": cancel_booking,
    "search_travel_policy": search_travel_policy,
}
```

---

### 💼 Product Manager View
The target product experience is a conversational assistant that acts with agency while providing complete transparency and control.

#### Key Product Journeys:
1. **Search & Refinement**: "Delhi to Goa this Saturday under 7k" → Agent checks missing parameters → Searches mock inventory → Ranks results based on user constraints → UI renders interactive flight cards.
2. **Comparison**: "Compare 1st and 3rd flight" → Agent generates side-by-side comparison table & explains trade-offs (price vs duration).
3. **Human-in-the-Loop Booking**: User clicks "Book flight" → Agent calculates exact breakdown (base fare + tax + baggage) → Displays modal dialog with full breakdown → Execution pauses until user clicks **[Confirm & Book]**.
4. **Developer Trace**: Toggle view showing real-time agent thoughts, tool calls, argument schemas, latencies, and token counts for technical interviews/demos.

---

## 2. Master Implementation Phases

### Phase 1: Backend Foundation (2-3 Days)
- FastAPI setup, PostgreSQL / SQLite database, SQLAlchemy models (`Flight`, `Booking`, `Passenger`, `User`, `Preference`).
- Seed script generating 500+ realistic mock flights.
- Deterministic API endpoints for `/flights/search`, `/flights/{id}`, `/bookings`.

### Phase 2: Flutter Travel UI (2-3 Days)
- Modern theme & responsive layout.
- Home screen, AI assistant chat interface, flight list view, detail sheet, booking summary card.

### Phase 3: LLM & Intent Engine (2-3 Days)
- Unified `LLMInterface` supporting Mistral AI API & Hugging Face inference.
- Structured output validation with Pydantic (`AgentIntent`, `TravelState`).

### Phase 4: Agent Orchestrator & Tool Loop (3-5 Days)
- Implement `while True` agent execution loop.
- Tool invocation layer with exception handling and failure recovery.

### Phase 5: Conversational Filter & Ranking (2-3 Days)
- State retention across turns for queries like "Show cheaper options" or "Only non-stop".
- Heuristic + LLM hybrid ranking system.

### Phase 6: Booking Agent & Human-in-the-Loop (2-3 Days)
- Re-check availability & fare calculation tools.
- Confirmation hand-off workflow (`POST /bookings/{id}/confirm`).

### Phase 7: Policy RAG Engine (2-3 Days)
- Markdown policy documents (baggage, refunds, cancellations).
- FAISS vector store & retriever tool (`search_travel_policy`).

### Phase 8: Contextual Memory & Personalization (1-2 Days)
- Short-term conversation session memory.
- Long-term user preferences (preferred cabin, non-stop preference, airline preference).

### Phase 9: SSE Streaming & Agent Observability (2-3 Days)
- Server-Sent Events endpoint (`/api/v1/chat/{session_id}/stream`).
- Flutter Agent Trace timeline screen.

### Phase 10: Evaluation, Guardrails & Polish (2 Days)
- Test suite evaluating intent accuracy, tool selection, error recovery, and booking safety.
- Documentation & interview demo script.
