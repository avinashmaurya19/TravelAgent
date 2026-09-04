# 📋 Workflow & Coding Standards (`standard.md`)

This rule file codifies the 4-phase Vibe Coding lifecycle protocol and general engineering standards.

---

## 1. The 4-Phase Vibe Coding Lifecycle

### Phase 1: Planning Phase
1. **Initiation**: Start feature discussions with *"Let's plan <feature name>, don't write code yet."*
2. **Context Review**: Examine relevant sections of [PRD.md](file:///Users/avinashmaurya/TravelAgent/PRD.md) and [PLANNING.md](file:///Users/avinashmaurya/TravelAgent/PLANNING.md).
3. **Draft Plan**: Outline technical requirements, API schemas, and UI designs.
4. **Document Plan**: Save the agreed plan to [PLANNING.md](file:///Users/avinashmaurya/TravelAgent/PLANNING.md).
5. **Task Listing**: Append actionable steps to [TASK.md](file:///Users/avinashmaurya/TravelAgent/TASK.md).

### Phase 2: Implementation Phase
1. **Incremental Coding**: Implement logic step-by-step.
2. **Review Diffs**: Verify generated code for correctness, type hints, and Pydantic validation.
3. **500-Line Check**: Ensure no file exceeds 500 lines. Refactor proactively.
4. **Mistake Logging**: If any error or misstep occurs, add the anti-pattern pattern to [.agents/rules/things-to-avoid.md](file:///Users/avinashmaurya/TravelAgent/.agents/rules/things-to-avoid.md).

### Phase 3: Test Phase
1. **Automated Testing**: Run unit tests (pytest for Python, flutter test for Dart).
2. **Empirical Verification**: Verify API responses and test failure recovery scenarios.

### Phase 4: Document Phase
1. **Update Task List**: Mark completed checklist items in [TASK.md](file:///Users/avinashmaurya/TravelAgent/TASK.md).
2. **Document Discoveries**: Record any new tasks found during development under `### Discovered During Work` in `TASK.md`.
3. **API & Readme Updates**: Update Swagger annotations, docstrings, and main project documentation.

---

## 2. General Code Quality Standards
- **Python Style**: PEP8 compliance, explicit type annotations, clear function docstrings.
- **Flutter Style**: Proper widget modularity, constant constructors (`const`), clean state separation.
- **Git Hygiene**: Atomic commits with clear descriptive commit messages matching feature steps.
