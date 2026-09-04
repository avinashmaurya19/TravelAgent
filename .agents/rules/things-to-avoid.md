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

