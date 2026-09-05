# 📋 TravelAgent AI — Task Tracking Checklist (`TASK.md`)

This checklist tracks tasks across the 10 implementation phases.
**Status Key**: `[ ]` Not Started | `[/]` In Progress | `[x]` Completed

---

## Phase 1: Backend Foundation (Deterministic Services)
- [x] Plan and structure Phase 1 Backend Foundation (Deterministic Services) (`2026-09-04`)
- [x] Initialize Python environment, FastAPI app structure, and requirements.txt (`2026-09-04`)
- [x] Create SQLAlchemy database models (`User`, `Flight`, `Booking`, `Passenger`, `UserPreference`, `Conversation`, `Message`) (`2026-09-04`)
- [x] Write `scripts/generate_flights.py` mock data generator (2,400+ realistic flight records across top Indian routes) (`2026-09-04`)
- [x] Implement deterministic flight search, detail, fare calculation, and booking endpoints (`2026-09-04`)
- [x] Add unit tests for flight repository search and filter functions (`2026-09-04`)

## Phase 2: Flutter Frontend Foundations
- [x] Initialize Flutter project `travel_agent_flutter` with clean feature-based architecture (`2026-09-05`)
- [x] Implement UI theme, typography, and responsive color palette (`2026-09-05`)
- [x] Create Home screen with quick prompt shortcuts ("Delhi to Goa weekend", "Delhi to Mumbai tomorrow") (`2026-09-05`)
- [x] Build Assistant Chat screen UI with chat bubbles and interactive flight cards (`2026-09-05`)
- [x] Create Flight Details modal sheet, Comparison view, and Booking Summary screen (`2026-09-05`)

## Phase 3: LLM Integration & Structured Intent Engine
- [x] Implement abstract `LLMInterface` class (`app/llm/base.py`) (`2026-09-05`)
- [x] Add `MistralLLM` provider implementation (`app/llm/mistral.py`) (`2026-09-05`)
- [x] Add `HuggingFaceLLM` provider implementation (`app/llm/huggingface.py`) (`2026-09-05`)
- [x] Create Pydantic schemas for `AgentIntent` and parameter extraction (`2026-09-05`)
- [x] Test intent recognition across sample user prompts (`2026-09-05`)

## Phase 4: Agent Orchestrator & Tool Calling Loop
- [x] Define `TravelState` Pydantic model for maintaining structured travel request context (`2026-09-05`)
- [x] Implement Python tool functions: `search_flights`, `filter_flights`, `get_flight_details`, `check_availability`, `calculate_fare`, `create_booking` (`2026-09-05`)
- [x] Build core `while True` agent execution loop in `app/agent/agent.py` (`2026-09-05`)
- [x] Add argument validation using Pydantic schemas and tool execution exception handling (`2026-09-05`)
- [x] Test end-to-end flight search tool invocation via agent loop (`2026-09-05`)
- [x] Connect Flutter `AssistantController` to `POST /api/v1/agent/chat` with tool badges & state synchronization (`2026-09-05`)

## Phase 5: Conversational Search & State Refinement
- [ ] Implement state retention logic to preserve origin/destination/dates during filter updates
- [ ] Support queries like "Show cheaper options", "Only non-stop", "What about tomorrow?"
- [ ] Implement flight comparison tool and Flutter side-by-side comparison table widget
- [ ] Implement deterministic + LLM explanation ranking engine

## Phase 6: Booking Agent & Human-in-the-Loop Dialogs
- [ ] Add pre-booking availability re-check (`check_availability`) and live fare breakdown (`calculate_fare`)
- [ ] Build Human-in-the-Loop confirmation workflow requiring explicit user approval
- [ ] Implement `POST /api/v1/bookings/{id}/confirm` backend handler and Flutter confirmation modal dialog
- [ ] Test price change handling during pre-booking check

## Phase 7: Travel Policy RAG Component
- [ ] Add markdown policy documents (`airline_baggage_policy.md`, `cancellation_policy.md`, `refund_policy.md`)
- [ ] Build FAISS vector store indexer using Sentence Transformers
- [ ] Implement `search_travel_policy` tool for answering policy questions with grounded retrieval
- [ ] Test RAG policy answers against ungrounded hallucinations

## Phase 8: Short-Term Memory & User Preferences
- [ ] Implement conversation message history store in PostgreSQL
- [ ] Implement user preference store (preferred cabin, preferred airlines, non-stop preference)
- [ ] Inject user preferences into flight ranking pipeline while respecting explicit user query overrides

## Phase 9: Real-Time SSE Streaming & Observability Trace
- [ ] Implement SSE endpoint (`GET /api/v1/chat/{session_id}/stream`) sending `tool_start`, `tool_result`, `assistant_message`
- [ ] Wire Flutter chat screen to listen to SSE events and show live execution indicators
- [ ] Build Developer Agent Trace screen in Flutter showing latency, tokens, tool args, and execution steps

## Phase 10: Evaluation, Guardrails & Demo Polish
- [ ] Implement evaluation test suite (Test cases 1–5 in PRD Section 44)
- [ ] Enforce guardrail validators (no direct DB access, tool whitelist, max file lines limit <500)
- [ ] Prepare comprehensive README, demo video guide, and technical interview talking points

---

## 🛠️ Discovered During Work
*New sub-tasks, edge cases, or refactoring tasks identified during implementation will be added below with timestamps.*

- [x] Resilient flight lookup: Support lookup by both primary UUID (`id`) and flight number (e.g. `AI-559`) in `FlightRepository` so users and LLM agents can query fare breakdown and availability seamlessly (`2026-09-05`)
