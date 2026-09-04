# ✈️ TravelAgent AI — Product Requirements Document (PRD)

## Project Overview

**TravelAgent AI** is a demo travel assistant inspired by platforms such as **ixigo**.

The goal is **not** to build a complete production-grade travel platform. The goal is to demonstrate how an **Agentic AI system** can interact with deterministic business services such as flight search, filtering, availability checking, fare calculation, and booking.

The application stack:
- **Flutter** — Mobile/Web frontend
- **Python + FastAPI** — Backend API & Agent Orchestration
- **Mistral AI / Hugging Face** — LLM Providers
- **PostgreSQL** — Application data & conversation persistence
- **FAISS** — Vector store for travel policy RAG
- **SSE (Server-Sent Events)** — Real-time streaming of agent execution events
- **Human-in-the-Loop** — Explicit confirmation before finalizing bookings

---

## 1. Project Vision

A user should be able to interact with the application naturally instead of filling out traditional flight search forms.

### Example Request
> *"I want to go from Delhi to Bangalore next Friday evening. My budget is around ₹8,000. I prefer a non-stop flight and I need one check-in bag."*

The AI Agent executes the following workflow:
1. Understand intent & extract structured parameters.
2. Identify missing parameters and ask clarifying questions if necessary.
3. Search flight inventory using deterministic tools.
4. Filter, rank, and explain recommendations.
5. Handle conversational refinements (e.g. *"Show cheaper options"*, *"Only non-stop"*).
6. Re-check real-time availability & calculate accurate fares before booking.
7. Collect passenger details & require explicit human confirmation before creating a mock booking.
8. Return PNR ticket confirmation.

---

## 2. Core Features & Concepts

- **Structured LLM Output & Intent Recognition**: Map raw queries to structured Pydantic models (`AgentIntent`, `TravelState`).
- **Deterministic Tool Calling**: Agent calls specific Python functions (`search_flights`, `filter_flights`, `check_availability`, `calculate_fare`, `create_booking`, `search_travel_policy`).
- **State Management & Conversational Refinement**: Retain state across turns so parameters like origin, destination, and dates persist when the user refines filters.
- **RAG Policy Engine**: Ground policy answers (baggage, refund, cancellation) using FAISS & markdown documentation.
- **Short-Term Memory & Long-Term Preferences**: Personalize ranking based on user preferences while prioritizing explicit turn requests.
- **Human-in-the-Loop Confirmation**: Never perform destructive/booking operations without explicit user confirmation in the UI.
- **Real-Time Streaming & Observability**: Stream agent events over SSE and present a developer trace screen showing tool calls, latency, token count, and parameters.

---

## 3. Technology Stack

### Backend
- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy & PostgreSQL
- FAISS & Sentence Transformers
- SSE (`sse-starlette`)

### Frontend
- Flutter (Dart)
- GetX (State Management, Routing, Dependency Injection)
- Dio HTTP Client
- EventSource / SSE Client

---

## 4. Development Roadmap (Phases 1–10)

- **Phase 1**: Backend Foundation (FastAPI, SQLite/PostgreSQL, Mock inventory)
- **Phase 2**: Flutter Travel UI (Home, Search, Cards, Booking dialogs)
- **Phase 3**: LLM Integration (Mistral/Hugging Face, Intent & Entity Extraction)
- **Phase 4**: Agent + Tools (Loop, tool registry, tool execution)
- **Phase 5**: Conversational Search & Filter Refinement
- **Phase 6**: Booking Workflow & Human-in-the-Loop Dialogs
- **Phase 7**: Policy RAG Component (FAISS index + retrieval)
- **Phase 8**: Short-Term Memory & User Preferences
- **Phase 9**: Streaming SSE & Observability Trace Screen
- **Phase 10**: Evaluation, Error Scenarios & Interview Demo Preparation
