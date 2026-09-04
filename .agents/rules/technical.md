# 🛠️ Technical Stack & Implementation Rules (`technical.md`)

This rule file defines technical constraints, library standards, state schemas, tool execution patterns, and safety guardrails.

---

## 1. Backend Standards
- **Framework**: Python 3.11+ with **FastAPI** and **Pydantic v2**.
- **Database Layer**: **SQLAlchemy 2.0+** ORM with Repository pattern (`FlightRepository`, `BookingRepository`).
- **Data Validation**: Every request/response body and tool argument must have an explicit Pydantic model.

---

## 2. Agent Orchestration Architecture

### Agent Loop (`app/agent/agent.py`)
```python
while True:
    response = llm.generate_response(messages=messages, tools=available_tools)
    
    if response.tool_call:
        tool_name = response.tool_call.name
        tool_args = response.tool_call.arguments
        
        # Execute validated tool
        result = execute_registered_tool(tool_name, tool_args)
        messages.append({"role": "tool", "content": result})
        continue
        
    return response.content
```

### Registered Tools Checklist
1. `search_flights(origin, destination, departure_date, passengers, cabin_class)`
2. `filter_flights(flights, max_price, max_stops, preferred_airline)`
3. `get_flight_details(flight_id)`
4. `check_availability(flight_id, passengers)`
5. `calculate_fare(flight_id, passengers, baggage, seat)`
6. `create_booking(flight_id, passenger_details, baggage, seat)`
7. `cancel_booking(booking_id)`
8. `search_travel_policy(question)`

---

## 3. RAG Engine Architecture
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (or lightweight alternative).
- **Vector Store**: **FAISS** index built on policy documents in `app/rag/documents/`.
- **Retrieval Protocol**: Query retrieved chunks → Inject as context → LLM formats grounded response.

---

## 4. Frontend Standards (Flutter)
- **State Management**: **GetX** (`GetxController`, `Rx` reactive properties, `GetBuilder`, `Bindings`, `GetMaterialApp` routing).
- **HTTP Client**: **Dio** with interceptors for error handling.
- **Real-Time SSE**: Stream events (`tool_start`, `tool_result`, `assistant_message`) to render active tool indicators and live agent trace timelines.

---

## 5. Security & Safety Guardrails
- **Tool Whitelist**: Only tools explicitly registered in `AVAILABLE_TOOLS` may be executed by the agent.
- **No Raw Database Queries**: The LLM agent MUST NEVER construct or run SQL strings directly.
- **Human-in-the-Loop Dialog**: Creating a booking (`create_booking`) produces a pending booking state and MUST await user approval via `POST /api/v1/bookings/{id}/confirm`.
- **Pre-Booking Verification**: Always run `check_availability` and `calculate_fare` immediately before confirmation to catch price changes or sold-out seats.
