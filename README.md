# ✈️ TravelAgent AI — Agentic Travel Assistant Demo

**TravelAgent AI** is an Agentic AI demo application inspired by travel platforms such as ixigo. It demonstrates how an LLM agent reasoningly orchestrates deterministic business microservices (flight search, filtering, availability checking, fare calculation, policy RAG, and booking) while preserving strict human-in-the-loop safety protocols.

---

## 🏗️ Architecture & Technology Stack

```text
                     ┌──────────────────────────┐
                     │  Flutter App (GetX)      │
                     │  Chat UI & Agent Trace   │
                     └────────────┬─────────────┘
                                  │ REST / SSE
                     ┌────────────▼─────────────┐
                     │     FastAPI Backend      │
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
                            └───────────┘
```

### Stack Highlights
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, PostgreSQL / SQLite.
- **AI Engine**: LLM Provider Abstraction (Mistral AI / Hugging Face), Pydantic State & Intent models, deterministic tool execution loop.
- **Policy RAG**: Sentence Transformers + FAISS vector search over markdown travel policies.
- **Real-Time Event Stream**: Server-Sent Events (SSE) for live tool activity & agent trace timelines.
- **Frontend**: Flutter (Dart) with **GetX** (State Management, Bindings, GetView, GetMaterialApp routing), Dio HTTP Client, and SSE EventSource client.

---

## 📁 Repository Structure

```text
TravelAgent/
├── GEMINI.md                     # Main Antigravity rule file (always active)
├── PRD.md                        # Complete Product Requirements Document
├── PLANNING.md                   # Architectural blueprint (Architect, Developer, PM)
├── TASK.md                       # Master checklist for tracking development progress
├── README.md                     # Project setup & execution guide
├── .gitignore                    # Environment & build ignores
├── .agents/
│   └── rules/                    # Antigravity rules directory
│       ├── awareness.md          # 500-line file limit & context rules
│       ├── project-structure.md  # Backend & Flutter directory layouts
│       ├── technical.md          # Tech stack, GetX, Pydantic & guardrails
│       ├── standard.md           # 4-Phase Vibe Coding lifecycle protocol
│       └── things-to-avoid.md    # Anti-patterns, scope boundaries & mistake log
└── .cursor/rules/                # Cursor AI rule mirrors (dual compatibility)
```

---

## 🚀 How to Run the Application

### 1. Backend Setup (`travel_agent_backend/`)
```bash
cd travel_agent_backend

# Create virtual environment & activate
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file & add API key (Mistral / HuggingFace)
cp .env.example .env

# Seed mock flight inventory
python scripts/generate_flights.py

# Run FastAPI dev server
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Frontend Setup (`travel_agent_flutter/`)
```bash
cd travel_agent_flutter

# Fetch Flutter dependencies
flutter pub get

# Run Flutter dev app (Web / iOS / Android)
flutter run
```

---

## 📊 How Progress is Tracked (`TASK.md`)

Progress is continuously tracked in **[TASK.md](file:///Users/avinashmaurya/TravelAgent/TASK.md)** across 10 implementation phases:

- `[ ]` Not Started
- `[/]` In Progress
- `[x]` Completed

Sub-tasks or edge-case handling discovered during development are appended under `### Discovered During Work` in `TASK.md`.

---

## 💬 How to Guide Antigravity AI to Work on Tasks

Follow the **4-Phase Vibe Coding Lifecycle** by giving prompts in natural language:

### 1. Start a New Phase / Feature (Planning Phase)
Prompt the AI:
> *"Let's plan Phase 1 (Backend Foundation), don't write code yet."*

Antigravity will inspect `PLANNING.md`, outline the file changes, update `PLANNING.md` and `TASK.md`, and present the plan for your approval.

### 2. Begin Coding (Implementation Phase)
Prompt the AI:
> *"The plan looks good. Please start implementing Phase 1 step 1."*

Antigravity will write modular code (ensuring no file exceeds 500 lines) and log any mistake patterns to `.agents/rules/things-to-avoid.md`.

### 3. Verify Implementation (Test Phase)
Prompt the AI:
> *"Run tests and verify backend endpoint responses."*

Antigravity will execute test suites or verification scripts to empirically prove code correctness.

### 4. Complete & Update Progress (Document Phase)
Prompt the AI:
> *"Mark Phase 1 tasks as completed in TASK.md and update API docs."*

Antigravity will check off completed items (`[x]`) in `TASK.md` and update documentation.
