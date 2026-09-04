# ✈️ TravelAgent AI — Agentic AI Demo Project

## Project Overview

**TravelAgent AI** is a demo travel assistant inspired by platforms such as **ixigo**.

The goal is **not** to build a complete production-grade travel platform. The goal is to demonstrate how an **Agentic AI system** can interact with deterministic business services such as flight search, filtering, availability checking, fare calculation, and booking.

The application will have:

- **Flutter** — mobile/web frontend
- **Python + FastAPI** — backend
- **Mistral AI or Hugging Face model** — LLM
- **PostgreSQL** — application data
- **FAISS** — vector search for RAG
- **Agent orchestration** — custom initially, optional LangGraph later
- **Mock flight inventory** — instead of real airline/GDS APIs
- **SSE/WebSocket** — streaming agent events
- **Human-in-the-loop confirmation** — required before booking

---

# 1. Project Vision

A user should be able to interact with the application naturally instead of filling out a traditional flight-search form.

### Example

> "I want to go from Delhi to Bangalore next Friday evening. My budget is around ₹8,000. I prefer a non-stop flight and I need one check-in bag."

The AI agent should:

1. Understand the request.
2. Extract the relevant travel information.
3. Identify missing information.
4. Ask clarification questions when necessary.
5. Search flight inventory using a tool.
6. Filter and rank available flights.
7. Explain the recommendations.
8. Handle follow-up requests conversationally.
9. Show flight details.
10. Re-check availability and price before booking.
11. Collect passenger information.
12. Ask for explicit user confirmation.
13. Create a mock booking.
14. Return a mock PNR/ticket.

The central idea is:

> **AI should reason about what needs to happen and use tools to perform deterministic business operations.**

---

# 2. What This Project Demonstrates

The project should demonstrate the following Agentic AI concepts:

- LLM integration
- Natural-language intent understanding
- Structured output
- Entity extraction
- Tool/function calling
- Agent loop
- Tool orchestration
- Conversational state
- Short-term memory
- Long-term user preferences
- RAG
- Human-in-the-loop workflows
- Guardrails
- Error recovery
- Streaming
- Agent observability/tracing
- LLM evaluation

The project should look less like:

```text
Flutter → ChatGPT → Response
```

and more like:

```text
Flutter
   ↓
FastAPI
   ↓
Agent Orchestrator
   ↓
LLM
   ↓
Tool Selection
   ↓
Tool Execution
   ↓
Tool Result
   ↓
LLM
   ↓
Next Action / Response
```

---

# 3. High-Level Architecture

```text
                    ┌──────────────────┐
                    │   Flutter App    │
                    │                  │
                    │ Chat             │
                    │ Flight Search    │
                    │ Flight Cards     │
                    │ Booking          │
                    └────────┬─────────┘
                             │
                        REST / SSE
                             │
                    ┌────────▼─────────┐
                    │     FastAPI      │
                    └────────┬─────────┘
                             │
                  ┌──────────▼──────────┐
                  │   Agent Orchestrator│
                  └──────────┬──────────┘
                             │
                       ┌─────▼─────┐
                       │    LLM    │
                       │ Mistral/HF│
                       └─────┬─────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
          Flight Tools     RAG        Memory
                │            │            │
                ▼            ▼            ▼
           PostgreSQL      FAISS      PostgreSQL
                │
                ▼
         Mock Flight Data

                    ┌──────────────────┐
                    │ Agent Trace /    │
                    │ Observability    │
                    └──────────────────┘
```

---

# 4. Recommended Technology Stack

## Frontend

- Flutter
- Dart
- BLoC or Riverpod
- Dio
- SSE or WebSocket client

Flutter is useful here because existing mobile-development experience can be reused while the main learning focus moves toward AI engineering.

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Redis (optional)

## AI

Primary option:

- Mistral AI

Alternative:

- Hugging Face hosted model

The AI layer should be abstracted so the model provider can be changed later.

Example:

```text
LLM Interface
      │
 ┌────┴─────┐
 │          │
Mistral   HuggingFace
```

## RAG

- Sentence Transformers or another embedding model
- FAISS
- Markdown/PDF/text policy documents

## Development

- Git
- Docker
- pytest
- Postman/Insomnia
- `.env` configuration

---

# 5. Core User Experience

## Home Screen

```text
--------------------------------
        TravelAgent AI

 Where do you want to go?

 [ ✨ Ask AI anything...       ]

 Popular destinations

 Delhi → Goa
 Delhi → Mumbai
 Delhi → Bangalore

 Recent searches
--------------------------------
```

The user can either:

- start a normal search
- use the AI assistant

---

# 6. AI Chat Experience

Example:

```text
--------------------------------
← AI Travel Assistant

AI:
Hi! Where would you like to fly?

YOU:
I want to go to Goa this weekend.

AI:
Sure! What city are you departing
from?

YOU:
Delhi.

AI:
Great. How many passengers?

YOU:
2 adults.
--------------------------------
```

The agent maintains the information collected so far.

---

# 7. Example Agent Conversation

### User

> I want to fly from Delhi to Goa this weekend under ₹7,000.

The agent identifies:

```text
Origin       = Delhi
Destination  = Goa
Date         = Missing
Budget       = ₹7,000
Passengers   = Missing
Cabin        = Missing
```

The agent should not blindly search.

It should ask:

> "Sure. Which date would you like to travel, and how many passengers?"

User:

> Saturday, one person.

Now the agent can search.

```text
User
 ↓
Agent
 ↓
search_flights()
 ↓
filter_flights()
 ↓
rank results
 ↓
Response
```

---

# 8. Agent State

Maintain structured state rather than relying only on chat history.

Example:

```python
class TravelState(BaseModel):

    origin: str | None = None
    destination: str | None = None
    departure_date: date | None = None

    passengers: int = 1
    cabin_class: str = "economy"

    max_price: float | None = None
    max_stops: int | None = None

    preferred_airline: str | None = None

    selected_flight_id: str | None = None

    passenger_details: dict | None = None

    booking_id: str | None = None
```

This state becomes the structured representation of the user's travel request.

---

# 9. Intent Detection

The system should support intents such as:

```text
SEARCH_FLIGHT
REFINE_SEARCH
FLIGHT_DETAILS
COMPARE_FLIGHTS
SELECT_FLIGHT
BOOK_FLIGHT
CHECK_BOOKING
CANCEL_BOOKING
TRAVEL_POLICY
GENERAL_TRAVEL
```

Examples:

> "Find me a flight from Delhi to Mumbai tomorrow."

→ `SEARCH_FLIGHT`

> "Show cheaper options."

→ `REFINE_SEARCH`

> "Compare the first and third."

→ `COMPARE_FLIGHTS`

> "What is the baggage allowance?"

→ `TRAVEL_POLICY`

> "Book the second one."

→ `BOOK_FLIGHT`

---

# 10. Structured LLM Output

Avoid asking the LLM for completely free-form interpretation.

Instead define a schema.

```python
class AgentIntent(BaseModel):

    intent: Literal[
        "SEARCH_FLIGHT",
        "REFINE_SEARCH",
        "FLIGHT_DETAILS",
        "COMPARE_FLIGHTS",
        "BOOK_FLIGHT",
        "CANCEL_BOOKING"
    ]

    origin: str | None
    destination: str | None
    date: str | None
    budget: float | None
```

The pipeline becomes:

```text
User Message
     ↓
LLM
     ↓
Structured JSON
     ↓
Pydantic Validation
     ↓
Agent
```

This gives the application predictable data instead of trusting arbitrary text.

---

# 11. Agent Tools

Start with approximately 6–8 tools.

## Tool 1 — Search Flights

```python
search_flights(
    origin,
    destination,
    departure_date,
    passengers,
    cabin_class
)
```

This tool searches the mock flight inventory.

---

## Tool 2 — Filter Flights

```python
filter_flights(
    flights,
    max_price=None,
    max_stops=None,
    preferred_airline=None
)
```

Example:

```text
All flights: 18
       ↓
Budget filter
       ↓
10 flights
       ↓
Non-stop filter
       ↓
6 flights
```

---

## Tool 3 — Get Flight Details

```python
get_flight_details(
    flight_id
)
```

Example response:

```json
{
  "flight_id": "6E-203",
  "airline": "IndiGo",
  "departure": "18:30",
  "arrival": "20:45",
  "duration": "2h 15m",
  "stops": 0,
  "price": 6840,
  "baggage": "15kg"
}
```

---

## Tool 4 — Check Availability

```python
check_flight_availability(
    flight_id,
    passengers
)
```

This should always happen again before booking.

The agent must not assume that an old search result is still available.

---

## Tool 5 — Calculate Fare

```python
calculate_fare(
    flight_id,
    passengers,
    baggage,
    seat
)
```

Example:

```json
{
  "base_fare": 5800,
  "taxes": 700,
  "baggage": 500,
  "seat": 300,
  "total": 7300
}
```

---

## Tool 6 — Create Booking

```python
create_booking(
    flight_id,
    passenger_details,
    baggage,
    seat
)
```

For this demo, use a mock booking service.

---

## Tool 7 — Cancel Booking

```python
cancel_booking(
    booking_id
)
```

This provides another agentic workflow.

---

## Tool 8 — Search Travel Policy

```python
search_travel_policy(
    question
)
```

This tool will use RAG.

---

# 12. Agent Loop

The core agent loop can conceptually look like:

```python
while True:

    response = llm(
        messages=messages,
        tools=available_tools
    )

    if response.tool_call:

        result = execute_tool(
            response.tool_call
        )

        messages.append(result)

        continue

    return response
```

Conceptually:

```text
             ┌───────────────┐
             │     User      │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │      LLM      │
             └───────┬───────┘
                     ↓
              Need a tool?
                /       \
              YES        NO
               ↓          ↓
         Execute tool   Response
               ↓
          Tool result
               ↓
              LLM
               ↑
               └────────────
```

This loop is one of the most important parts of the project.

---

# 13. Flight Search Flow

Example:

> "Find me a cheap flight Delhi to Mumbai tomorrow."

```text
User
 ↓
LLM
 ↓
Extract parameters
 ↓
Agent state
 ↓
search_flights()
 ↓
Flight database
 ↓
Search result
 ↓
filter_flights()
 ↓
Ranking
 ↓
LLM
 ↓
Flutter flight cards
```

---

# 14. AI-Based Ranking

The AI should not only return raw search results.

Suppose the API returns:

```text
Flight A
₹6,500
7:00 AM
1h 50m

Flight B
₹6,900
6:30 PM
2h 10m

Flight C
₹5,900
10:00 PM
2h 15m
```

The user said:

> "Evening flight under ₹7,000."

The agent should recognize Flight B as a strong match.

Ranking can consider:

```text
Price
Departure time
Duration
Stops
Airline
Baggage
Refundability
Seat availability
User preferences
```

For the demo, start with deterministic ranking rules and optionally let the LLM explain the ranking.

Example:

> "Flight B is the best match because it is an evening, non-stop flight within your ₹7,000 budget."

---

# 15. Conversational Refinement

This is critical.

The user should be able to say:

> "Show cheaper flights."

The system must retain:

```text
Origin      = Delhi
Destination = Goa
Date        = Saturday
Passengers  = 1
```

Only the relevant filter changes.

Other examples:

> "Only non-stop."

> "What about tomorrow?"

> "Show evening flights."

> "Show flights with 15kg baggage."

> "Compare the first and third."

This demonstrates conversational agent behavior.

---

# 16. Flight Comparison

User:

> "Compare the first and third flights."

The agent retrieves details and produces structured comparison data.

| Attribute | Flight 1 | Flight 3 |
|---|---:|---:|
| Price | ₹6,840 | ₹5,900 |
| Duration | 2h 15m | 3h 05m |
| Stops | 0 | 1 |
| Baggage | 15kg | 15kg |

Then the AI can explain:

> "Flight 3 is cheaper by ₹940, but Flight 1 is faster and non-stop."

Flutter should render this as a proper comparison UI rather than only displaying text.

---

# 17. Booking Workflow

Once the user selects a flight:

```text
Flight Details
      ↓
Passenger Details
      ↓
Add-ons
      ↓
Fare Summary
      ↓
Availability Check
      ↓
AI Confirmation
      ↓
Human Approval
      ↓
Mock Payment
      ↓
Booking
```

---

# 18. Human-in-the-Loop

This is one of the strongest parts of the demo.

The agent must not silently book a flight.

Example:

```text
Flight: 6E203
Delhi → Goa
18:30 → 20:45

Fare: ₹6,840
Baggage: 15kg

Total: ₹7,340
```

AI:

> "I've prepared the booking. The total is ₹7,340. Would you like me to confirm the booking?"

Flutter:

```text
┌──────────────────────────────┐
│ Confirm Booking              │
│                              │
│ DEL → GOI                    │
│ 6E203                        │
│                              │
│ Total: ₹7,340                │
│                              │
│ [ Cancel ] [ Confirm & Book ]│
└──────────────────────────────┘
```

Only after the user presses **Confirm & Book**:

```text
Flutter
 ↓
POST /bookings/{id}/confirm
 ↓
FastAPI
 ↓
Validate
 ↓
Check availability
 ↓
Create booking
 ↓
Return PNR
```

---

# 19. Fare Change Handling

The demo should intentionally simulate real-world problems.

Example:

Initial search:

```text
₹6,840
```

Before booking:

```text
₹7,240
```

Agent:

> "The flight price has changed from ₹6,840 to ₹7,240. Would you like to continue?"

This demonstrates that the agent uses fresh deterministic data before taking an action.

---

# 20. Mock Flight Database

Do not integrate real airline/GDS booking APIs initially.

Create realistic mock inventory.

Target:

```text
500–5000 flights
```

Data fields:

```text
flight_id
airline
flight_number
origin
destination
departure_time
arrival_time
duration
stops
base_price
baggage
available_seats
refundable
```

Example routes:

```text
DEL → BOM
DEL → BLR
DEL → GOI
DEL → HYD
DEL → MAA

BOM → DEL
BOM → BLR
BOM → GOI
...
```

Use realistic prices, times, airlines, and availability.

---

# 21. Repository Architecture

Create an abstraction for flight inventory.

```python
class FlightRepository:
    def search_flights(...):
        pass
```

Initial implementation:

```python
class MockFlightRepository(FlightRepository):
    ...
```

Later:

```python
class RealFlightRepository(FlightRepository):
    ...
```

The agent should not care where flight data comes from.

This makes the architecture cleaner and easier to explain in interviews.

---

# 22. Database Design

Keep the initial schema simple.

## users

```text
id
name
email
```

## flights

```text
id
airline
flight_number
origin
destination
departure_time
arrival_time
duration
stops
base_price
baggage
available_seats
```

## bookings

```text
id
user_id
flight_id
status
total_amount
pnr
created_at
```

## passengers

```text
id
booking_id
name
date_of_birth
passport_number
```

## conversations

```text
id
user_id
session_id
created_at
```

## messages

```text
id
conversation_id
role
content
created_at
```

## user_preferences

```text
id
user_id
preferred_cabin
preferred_airlines
prefers_non_stop
preferred_departure
```

---

# 23. RAG Component

Add a small RAG system for travel policies.

Documents:

```text
airline_baggage_policy.md
cancellation_policy.md
refund_policy.md
airport_guidelines.md
travel_documents.md
```

Pipeline:

```text
Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
FAISS
    ↓
Retriever
    ↓
Relevant Context
    ↓
LLM
    ↓
Answer
```

Example:

> "Can I carry a power bank on this flight?"

Agent:

```text
search_travel_policy()
       ↓
retrieve relevant policy
       ↓
LLM
       ↓
Answer
```

The answer should be grounded in the retrieved policy rather than relying purely on model knowledge.

---

# 24. Memory

Implement two types of memory.

## Short-Term Memory

Current conversation:

```text
Delhi → Goa
Saturday
2 adults
₹7,000
Non-stop
```

## Long-Term Preferences

Example:

```json
{
  "preferred_cabin": "economy",
  "preferred_airlines": ["IndiGo"],
  "prefers_non_stop": true,
  "preferred_departure": "evening"
}
```

If the user later says:

> "Find me a flight to Mumbai."

The agent can use these preferences when ranking.

Important:

> Explicit instructions from the current user request should override stored preferences.

---

# 25. Streaming

Implement streaming responses.

Instead of:

```text
User
 ↓
Wait
 ↓
Complete response
```

use:

```text
User
 ↓
Agent
 ↓
Streaming events
 ↓
Flutter
```

Example:

```text
✓ Understanding your request
✓ Searching flights
✓ Found 18 flights
✓ Applying your preferences
✓ Comparing results
✓ Preparing recommendations
```

Use:

- SSE for simplicity
- WebSocket if you want bidirectional event handling

For this project, SSE is a good first choice.

---

# 26. Agent Events

Stream structured events rather than only text.

Example:

```json
{
  "type": "tool_start",
  "tool": "search_flights"
}
```

Then:

```json
{
  "type": "tool_result",
  "tool": "search_flights",
  "count": 18
}
```

Then:

```json
{
  "type": "assistant_message",
  "content": "I found 18 flights."
}
```

Flutter can render these events differently.

---

# 27. Agent Trace / Observability

Create a developer-only screen.

Example:

```text
Agent Trace

Session: 83A21

User request
    ↓
Intent extraction
    ↓
search_flights()
    ↓
18 results
    ↓
filter_flights()
    ↓
7 results
    ↓
rank flights
    ↓
3 recommendations
    ↓
User selection
    ↓
check_availability()
    ↓
calculate_fare()
    ↓
Human approval
    ↓
create_booking()
```

Display:

```text
Model
Latency
Tool calls
Tool arguments
Tool results
Errors
Token usage
```

This is extremely useful for debugging and demonstrates production-oriented thinking.

---

# 28. Guardrails

Implement explicit safety and correctness rules.

## Guardrail 1 — No direct database access by LLM

The LLM can only call registered tools.

```python
AVAILABLE_TOOLS = {
    "search_flights": search_flights,
    "get_flight_details": get_flight_details,
    "check_availability": check_availability,
    "calculate_fare": calculate_fare,
    "create_booking": create_booking
}
```

## Guardrail 2 — Booking requires confirmation

Never automatically finalize a booking.

## Guardrail 3 — Validate tool arguments

Use Pydantic.

## Guardrail 4 — Re-check price

Before booking:

```text
check_availability()
calculate_fare()
```

## Guardrail 5 — Tool whitelist

Only known tools can be executed.

---

# 29. Error Recovery

Intentionally support failures.

### Flight API unavailable

> "I couldn't retrieve flight availability right now. Please try again."

### Flight sold out

> "That flight is no longer available. I found two similar options."

### Price changed

> "The fare changed from ₹6,840 to ₹7,240. Would you like to continue?"

### Invalid passenger details

> "The passenger date of birth is invalid. Please check the information and try again."

This demonstrates agent recovery rather than only successful paths.

---

# 30. API Design

## Chat

```http
POST /api/v1/chat
```

Request:

```json
{
  "session_id": "abc123",
  "message": "Find a flight from Delhi to Goa tomorrow"
}
```

## Flight Search

```http
POST /api/v1/flights/search
```

## Flight Details

```http
GET /api/v1/flights/{flight_id}
```

## Booking

```http
POST /api/v1/bookings
```

## Confirm Booking

```http
POST /api/v1/bookings/{id}/confirm
```

## Booking Status

```http
GET /api/v1/bookings/{id}
```

## Cancel Booking

```http
POST /api/v1/bookings/{id}/cancel
```

## Agent Stream

```http
GET /api/v1/chat/{session_id}/stream
```

---

# 31. Flutter Screens

Recommended screens:

```text
1. Splash
2. Home
3. AI Travel Assistant
4. Flight Search Results
5. Flight Details
6. Flight Comparison
7. Passenger Details
8. Fare Summary
9. Booking Confirmation
10. Booking Success
11. My Trips
12. Developer / Agent Trace
```

The primary experience should remain the AI travel assistant.

---

# 32. Flight Result UI

Example:

```text
┌─────────────────────────────────┐
│ ✈ IndiGo 6E-203                 │
│                                 │
│ DEL 18:30 ─────── 20:45 GOI     │
│       2h 15m • Non-stop         │
│                                 │
│ ₹6,840 / passenger              │
│ 15kg baggage                    │
│                                 │
│ ⭐ Best match                   │
│                                 │
│          View details           │
└─────────────────────────────────┘
```

AI explanation:

> "This is the best match because it fits your ₹7,000 budget and is non-stop."

---

# 33. Mock Payment

Do not build a real payment gateway.

Create:

```text
Mock Payment Gateway
```

Flow:

```text
Fare confirmation
      ↓
Mock payment
      ↓
Payment success
      ↓
Booking created
```

This keeps the project focused on Agentic AI.

---

# 34. Project Folder Structure

Recommended backend:

```text
travel_agent_backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── chat.py
│   │   ├── flights.py
│   │   └── bookings.py
│   │
│   ├── agent/
│   │   ├── agent.py
│   │   ├── state.py
│   │   ├── prompts.py
│   │   ├── intents.py
│   │   └── tools/
│   │       ├── flight_search.py
│   │       ├── flight_details.py
│   │       ├── filtering.py
│   │       ├── availability.py
│   │       ├── fare.py
│   │       └── booking.py
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── mistral.py
│   │   └── huggingface.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── documents/
│   │
│   ├── memory/
│   │   ├── conversation.py
│   │   └── preferences.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── repositories/
│   │
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── flight.py
│   │   └── booking.py
│   │
│   └── services/
│       └── ranking.py
│
├── tests/
│
├── data/
│   └── flights.json
│
├── scripts/
│   └── generate_flights.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

Recommended Flutter structure:

```text
travel_agent_flutter/
│
├── lib/
│   ├── main.dart
│   │
│   ├── core/
│   │   ├── network/
│   │   ├── theme/
│   │   └── constants/
│   │
│   ├── features/
│   │   ├── home/
│   │   ├── assistant/
│   │   ├── flights/
│   │   ├── booking/
│   │   ├── trips/
│   │   └── agent_trace/
│   │
│   ├── models/
│   ├── repositories/
│   └── services/
│
└── test/
```

---

# 35. Development Phases

## Phase 1 — Backend Foundation

Estimated: **2–3 days**

Build:

```text
FastAPI
PostgreSQL
SQLAlchemy
Pydantic
Flight model
Booking model
Flight search API
Mock booking API
```

No AI yet.

Goal:

> Build a reliable deterministic travel backend first.

---

# 36. Phase 2 — Flutter Travel UI

Estimated: **2–3 days**

Build:

```text
Home
Search
Flight cards
Flight details
Passenger details
Fare summary
Booking confirmation
Booking success
```

Goal:

> The application should already work without AI.

---

# 37. Phase 3 — LLM Integration

Estimated: **2–3 days**

Add:

```text
Mistral / Hugging Face
Structured output
Intent detection
Entity extraction
```

Example:

```text
"I need a flight from Delhi to Goa tomorrow"
```

becomes:

```json
{
  "intent": "SEARCH_FLIGHT",
  "origin": "DEL",
  "destination": "GOI",
  "date": "tomorrow",
  "passengers": null
}
```

Goal:

> Understand natural-language travel requests.

---

# 38. Phase 4 — Agent + Tools

Estimated: **3–5 days**

Implement:

```text
LLM
 ↓
Tool selection
 ↓
Tool execution
 ↓
Tool result
 ↓
LLM
```

Tools:

```text
search_flights
get_flight_details
filter_flights
check_availability
calculate_fare
```

Goal:

> Demonstrate actual agentic behavior.

---

# 39. Phase 5 — Conversational Search

Estimated: **2–3 days**

Support:

```text
"Show cheaper options."

"Only non-stop."

"What about tomorrow?"

"Show evening flights."

"Compare first and third."

"Show flights with baggage included."
```

Goal:

> Demonstrate conversation state and iterative planning.

---

# 40. Phase 6 — Booking Agent

Estimated: **2–3 days**

Implement:

```text
Select flight
 ↓
Passenger details
 ↓
Fare calculation
 ↓
Availability check
 ↓
Human confirmation
 ↓
Mock payment
 ↓
Booking
```

Goal:

> Demonstrate an agent that can safely perform an action.

---

# 41. Phase 7 — RAG

Estimated: **2–3 days**

Add:

```text
Policy documents
 ↓
Chunking
 ↓
Embeddings
 ↓
FAISS
 ↓
Retriever
 ↓
LLM
```

Support:

```text
Baggage
Refund
Cancellation
Travel documents
Airport policies
```

Goal:

> Demonstrate grounded generation.

---

# 42. Phase 8 — Memory

Estimated: **1–2 days**

Implement:

```text
Conversation memory
User preferences
```

Goal:

> Demonstrate persistent user context.

---

# 43. Phase 9 — Streaming + Observability

Estimated: **2–3 days**

Add:

```text
SSE
Agent events
Tool execution events
Latency
Token usage
Errors
Agent trace
```

Goal:

> Make the project feel like a real AI application rather than a prototype chatbot.

---

# 44. Phase 10 — Evaluation

Estimated: **2 days**

Create test cases.

### Test 1

Input:

> "Delhi to Mumbai tomorrow."

Expected:

```text
Ask for passenger count
```

### Test 2

Input:

> "Delhi to Mumbai tomorrow for 2 people."

Expected:

```text
Search flights
```

### Test 3

Input:

> "Show cheaper options."

Expected:

```text
Maintain previous route/date/passengers
```

### Test 4

Input:

> "Book the second flight."

Expected:

```text
Identify flight #2
```

### Test 5

Input:

> "Book it."

Expected:

```text
Require booking confirmation
```

Track:

```text
Intent accuracy
Tool selection accuracy
Tool argument accuracy
Booking success rate
Hallucination/error rate
```

---

# 45. Suggested 4-Week Timeline

## Week 1 — Product + Backend

```text
Day 1
Project setup
Architecture
Database

Day 2
Flight schema
Mock flight data

Day 3
Flight search API

Day 4
Flight details
Filtering

Day 5
Booking API

Day 6
Error handling
Testing

Day 7
Cleanup
```

---

## Week 2 — Flutter + LLM

```text
Day 8
Flutter project architecture

Day 9
Home + search UI

Day 10
Flight result UI

Day 11
Flight details + booking UI

Day 12
LLM integration

Day 13
Structured output

Day 14
Intent/entity extraction
```

---

## Week 3 — Agent

```text
Day 15
Agent state

Day 16
Tool definitions

Day 17
Tool calling

Day 18
Agent loop

Day 19
Conversational refinement

Day 20
Flight ranking

Day 21
Booking agent + human approval
```

---

## Week 4 — Advanced AI Features

```text
Day 22
RAG

Day 23
Memory

Day 24
SSE streaming

Day 25
Agent events

Day 26
Agent trace

Day 27
Evaluation

Day 28
Error scenarios

Day 29
UI polish

Day 30
README + demo video + interview preparation
```

---

# 46. What NOT to Build

Avoid spending time on:

- Real airline booking
- Real payment gateway
- Complete hotel booking
- Bus booking
- Train booking
- Complex authentication
- Large admin dashboard
- Hundreds of APIs
- Production-grade distributed infrastructure

The objective is not:

> "I cloned ixigo."

The objective is:

> "I built an AI agent that can interact with deterministic travel systems."

---

# 47. Final Demo Flow

The final demo should be approximately **5–10 minutes**.

## Demo 1 — Natural-language search

User:

> "I want to fly from Delhi to Bangalore next Friday evening under ₹8,000."

Agent:

```text
Understands request
        ↓
Checks missing information
        ↓
Searches flights
        ↓
Filters flights
        ↓
Ranks flights
        ↓
Displays recommendations
```

---

## Demo 2 — Conversational refinement

User:

> "Only non-stop flights."

Agent updates the search.

Then:

> "Show me the cheaper ones."

Agent maintains the context.

---

## Demo 3 — Comparison

User:

> "Compare the first and third."

Agent returns a structured comparison.

---

## Demo 4 — Booking

User:

> "Book the first one."

Agent:

```text
Check availability
 ↓
Calculate current fare
 ↓
Prepare booking
 ↓
Ask for confirmation
```

Flutter:

```text
Confirm booking for ₹7,420?

[ Cancel ] [ Confirm & Book ]
```

User confirms.

---

## Demo 5 — Booking result

```text
Booking successful 🎉

PNR: X7K2P9

DEL → BLR
11 Sep 2026

Passenger: Avinash
Status: Confirmed
```

---

# 48. Interview Explanation

You should eventually be able to explain the project like this:

> **"I built an AI-powered travel agent inspired by platforms like ixigo. Instead of using an LLM only as a chatbot, I designed an agentic workflow where the LLM understands the user's intent, maintains structured travel state, selects tools, executes flight-search and booking operations, and uses the returned data to decide the next action.**
>
> **The flight inventory and booking operations are deterministic backend services, while the LLM acts as the reasoning and orchestration layer. I also implemented RAG for travel policies, conversational memory, streaming agent events, observability, guardrails, and human-in-the-loop confirmation before booking."**

That is a much stronger explanation than:

> "I created a Flutter app and integrated Mistral."

---
