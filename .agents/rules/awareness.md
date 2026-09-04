# 🔄 Project Awareness & Context Rules (`awareness.md`)

This rule file defines standards for project context, file size limits, code modularity, and task state tracking.

---

## 1. Project Awareness & Context
- **Ground Context**: Always read [PLANNING.md](file:///Users/avinashmaurya/TravelAgent/PLANNING.md) at the start of a session or prior to planning features to understand system architecture.
- **Check Task List**: Always inspect [TASK.md](file:///Users/avinashmaurya/TravelAgent/TASK.md) before starting a new task. If the task is not listed, add it with a brief description and date.
- **Consistent Naming & Conventions**: Follow domain naming abstractions consistently across backend and frontend (`FlightRepository`, `TravelState`, `AgentIntent`, `search_flights`, `create_booking`).

---

## 2. Code Structure & Modularity
- **500-Line Limit**: **Never create or edit a file to exceed 500 lines of code.**
  - If a file approaches 500 lines, immediately refactor by extracting helper classes, tools, services, or sub-widgets into separate modules.
- **Modular Organization**: Group code logically into small, single-responsibility files (e.g. separate tool functions in `app/agent/tools/`, separate feature widgets in Flutter).
- **Clean Imports**: Use clear, consistent imports (prefer relative imports within backend packages; follow Dart package import guidelines in Flutter).

---

## 3. Task Completion Protocol
- **Immediate Task Checkoff**: Mark completed tasks in [TASK.md](file:///Users/avinashmaurya/TravelAgent/TASK.md) (`[x]`) immediately upon completing and verifying them.
- **Discovered Sub-tasks**: Add any new sub-tasks, bugs, or refactoring ideas discovered during work under the `### Discovered During Work` section in `TASK.md`.
- **Living Learnings**: If a mistake or edge-case failure occurs during implementation, log the pattern in [.agents/rules/things-to-avoid.md](file:///Users/avinashmaurya/TravelAgent/.agents/rules/things-to-avoid.md).
