---
trigger: always_on
---

# ⚠️ Things to Avoid — Anti-Patterns & Scope Boundaries (`things-to-avoid.md`)

This rule file records strict anti-patterns, scope boundaries, and project pitfalls. It is a **living document** that must be updated whenever a mistake or edge-case failure occurs.

---

## 1. Product Scope Anti-Patterns ("What NOT to Build")
- ❌ **Do NOT integrate real airline or GDS APIs** (Amadeus, Sabre, etc.). Use realistic mock flight inventory.
- ❌ **Do NOT integrate real payment gateways** (Stripe, Razorpay). Use a mock payment service.
- ❌ **Do NOT expand scope into hotel, train, or bus bookings.** Focus strictly on flight assistant capabilities.
- ❌ **Do NOT spend time building complex user auth or admin portals.** Focus core effort on agent intelligence, tool execution, and UI presentation.

---

## 2. Technical & Architecture Anti-Patterns
- ❌ **NEVER allow the LLM to access the database directly.** The LLM must call registered Pydantic tool functions.
- ❌ **NEVER execute a booking automatically without explicit human confirmation.** Always mandate `POST /confirm` via interactive UI dialog.
- ❌ **NEVER create or edit a file to exceed 500 lines of code.** Refactor into smaller sub-modules immediately.
- ❌ **NEVER rely on stale search prices for booking.** Always execute `check_availability` and `calculate_fare` prior to confirmation.
- ❌ **NEVER return ungrounded travel policy answers.** Use the FAISS policy retriever tool for baggage, refund, and cancellation questions.
- ❌ **NEVER make unverified code changes.** Always run verification tests or API calls to prove functionality.
- ❌ **Never set version number in requirements.txt file.
---

## 3. Discovered Mistake Log
*(Add new recurring mistakes or bug patterns here as they are discovered during development)*

- *Initial setup: Ensure workspace files are created without artifact metadata parameter in Antigravity tools.*
- *Pydantic validation: When using Pydantic's `EmailStr`, ensure `email-validator` is present in requirements.*
- *Flight identifiers: Flight lookups should gracefully support both unique database UUID (`id`) and human/agent-friendly `flight_number` (e.g. `AI-559`), preventing 404 errors when flight numbers are supplied.*
- *Android physical device testing: `10.0.2.2` only exists in emulators. For physical devices attached via USB, run `adb reverse tcp:8000 tcp:8000` and route requests through `http://127.0.0.1:8000/api/v1`.*
- *Mistral AI models: Free-tier accounts on Mistral have a rate limit of 0 requests/min on commercial models like `mistral-small-latest`, returning 429. Use `open-mistral-nemo` or `open-mistral-7b` which are fully active and free.*
- *Mistral Tool Calling Message Formatting: In multi-turn dialogs, an assistant message that invoked tools must include the `tool_calls` list with valid `id` and `function` arguments. Subsequent `tool` role messages must supply matching `tool_call_id` and `name` attributes, otherwise Mistral API rejects the payload with `400 Bad Request`.*
- *Multi-turn Conversational Context & Booking Triggers: The client must pass recent conversation history (`chat_history`) to `/api/v1/agent/chat` so the LLM remembers previous assistant questions and user answers. When a user prompt expresses booking intent (e.g. 'book', 'confirm'), the UI must suppress opening comparison sheets, and the agent system prompt must prioritize calling `create_booking` directly on the active flight rather than falling back to `compare_flights`.*
- *Open-Ended Destination Fan-Out & Tool Badge Clutter: When a user query specifies 'anywhere' or leaves the destination open, the LLM agent must not fan out 10–15 parallel search queries across all database airports, which wastes context tokens and clutters the UI. Limit open-ended searches to top 2–3 destinations (e.g. BOM, BLR, GOI) and prompt the user for their preferred region. In the Flutter chat UI, aggregate multiple tool executions of the same tool name into a consolidated count badge.*
- *Open-Ended Date Probing & Empty Recommendations Fallback: When a user asks for 'any date in month X', the LLM agent must not sequentially probe 5+ individual dates in a tight loop until hitting max_iterations. Limit date probing to 1–2 dates, instruct the LLM to stop if results are zero, and never output 'Please see the recommendations above' if no flights were actually found; instead output a clear route-aware explanation of available network hubs.*

