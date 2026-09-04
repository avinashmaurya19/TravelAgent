# 📁 Project Structure Rules (`project-structure.md`)

This rule file codifies the explicit directory layout and file organization guidelines for both the backend and frontend.

---

## 1. Backend Directory Structure (`travel_agent_backend/`)

```text
travel_agent_backend/
│
├── app/
│   ├── main.py                    # FastAPI entrypoint & router initialization
│   │
│   ├── api/                       # API Route Controllers
│   │   ├── chat.py                # Chat & SSE streaming endpoints
│   │   ├── flights.py             # Flight search & detail endpoints
│   │   └── bookings.py            # Booking & confirmation endpoints
│   │
│   ├── agent/                     # Agent Orchestration Core
│   │   ├── agent.py               # Core while-loop agent orchestrator
│   │   ├── state.py               # TravelState Pydantic model
│   │   ├── prompts.py             # System prompts & tool instructions
│   │   ├── intents.py             # AgentIntent Pydantic model
│   │   └── tools/                 # Registered Agent Tools
│   │       ├── flight_search.py   # search_flights tool
│   │       ├── flight_details.py  # get_flight_details tool
│   │       ├── filtering.py       # filter_flights tool
│   │       ├── availability.py    # check_availability tool
│   │       ├── fare.py            # calculate_fare tool
│   │       └── booking.py         # create_booking tool
│   │
│   ├── llm/                       # Provider Abstraction Layer
│   │   ├── base.py                # Abstract LLMInterface
│   │   ├── mistral.py             # Mistral AI implementation
│   │   └── huggingface.py         # Hugging Face implementation
│   │
│   ├── rag/                       # Policy RAG Component
│   │   ├── embeddings.py          # Sentence Transformer embeddings
│   │   ├── retriever.py           # FAISS vector store retriever
│   │   └── documents/             # Markdown policy docs
│   │
│   ├── memory/                    # Context Persistence
│   │   ├── conversation.py        # Short-term session memory
│   │   └── preferences.py         # Long-term user preferences
│   │
│   ├── database/                  # Data Layer
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── session.py             # DB connection & session factory
│   │   └── repositories/          # Repository patterns (Flight, Booking)
│   │
│   ├── schemas/                   # Pydantic Request/Response Schemas
│   │   ├── chat.py
│   │   ├── flight.py
│   │   └── booking.py
│   │
│   └── services/                  # Business Logic & Ranking
│       └── ranking.py             # Flight ranking algorithms
│
├── tests/                         # Pytest test suite
├── data/
│   └── flights.json               # Seed mock flight data
├── scripts/
│   └── generate_flights.py        # Mock inventory generator script
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 2. Frontend Directory Structure (`travel_agent_flutter/`)

```text
travel_agent_flutter/
│
├── lib/
│   ├── main.dart                  # App entrypoint & GetMaterialApp configuration
│   │
│   ├── core/                      # Core infrastructure
│   │   ├── network/               # Dio HTTP client & SSE listener
│   │   ├── theme/                 # App colors, fonts, styles
│   │   ├── routes/                # GetX AppPages & AppRoutes definitions
│   │   └── constants/             # API URLs & constants
│   │
│   ├── features/                  # GetX Feature Modules
│   │   ├── home/                  # Home (home_view.dart, home_controller.dart, home_binding.dart)
│   │   ├── assistant/             # Assistant (assistant_view.dart, assistant_controller.dart, assistant_binding.dart)
│   │   ├── flights/               # Flights (flights_view.dart, flights_controller.dart, flights_binding.dart)
│   │   ├── booking/               # Booking dialogs (booking_view.dart, booking_controller.dart, booking_binding.dart)
│   │   ├── trips/                 # My Trips (trips_view.dart, trips_controller.dart, trips_binding.dart)
│   │   └── agent_trace/           # Developer Agent Trace (trace_view.dart, trace_controller.dart, trace_binding.dart)
│   │
│   ├── models/                    # Data models & JSON serialization
│   ├── repositories/              # API repository handlers
│   └── services/                  # Global GetX services (e.g. AuthService, StorageService)
│
└── test/                          # Flutter unit & widget tests
```

---

## 3. Placement Rules
- New API routes MUST be placed under `app/api/`.
- New agent tools MUST be placed under `app/agent/tools/`.
- New Flutter features MUST be structured under `lib/features/<feature_name>/`.
- Never dump miscellaneous files into root folders.
