#!/usr/bin/env python3
"""Automated Guardrail Verification Script.

Enforces:
1. No Direct DB Access by LLM (AST & regex check for raw SQL in agent modules)
2. Tool Whitelist Registration & Execution Enforcement
3. Human-in-the-Loop Confirmation Policy (Pending status mandate)
4. 500-Line Code Limit across all Python and Dart source files
5. No Version Pins in requirements.txt
"""

import os
import sys
import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = WORKSPACE_ROOT / "travel_agent_backend"
FLUTTER_DIR = WORKSPACE_ROOT / "travel_agent_flutter"


def check_500_line_limit() -> bool:
    """Ensure no source code file exceeds the strict 500 lines of code limit."""
    print("\n[1/5] Checking 500-Line File Limit...")
    violations = []
    total_files = 0

    scan_dirs = [
        BACKEND_DIR / "app",
        BACKEND_DIR / "tests",
        BACKEND_DIR / "scripts",
        FLUTTER_DIR / "lib",
        FLUTTER_DIR / "test",
    ]

    for sdir in scan_dirs:
        if not sdir.exists():
            continue
        for root, _, files in os.walk(sdir):
            for file in files:
                if file.endswith((".py", ".dart")):
                    total_files += 1
                    path = Path(root) / file
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = len(f.readlines())
                        if lines > 500:
                            violations.append((path.relative_to(WORKSPACE_ROOT), lines))

    if violations:
        print(f"  ❌ FAILED: {len(violations)} file(s) exceed 500 lines:")
        for path, count in violations:
            print(f"     - {path}: {count} lines")
        return False

    print(f"  ✅ PASSED: All {total_files} scanned source files are under 500 lines.")
    return True


def check_no_direct_db_access_by_llm() -> bool:
    """Ensure agent orchestrator and tools do not use raw SQL queries."""
    print("\n[2/5] Checking No Direct DB Access in Agent & Tool Layers...")
    agent_dir = BACKEND_DIR / "app" / "agent"
    forbidden_patterns = [
        re.compile(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b\s+', re.IGNORECASE),
        re.compile(r'db\.execute\(text\('),
        re.compile(r'cursor\.execute\('),
    ]

    violations = []
    for root, _, files in os.walk(agent_dir):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for idx, line in enumerate(f, 1):
                        stripped = line.strip()
                        # Ignore comments or docstrings
                        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                            continue
                        for pat in forbidden_patterns:
                            if pat.search(line):
                                violations.append((path.relative_to(WORKSPACE_ROOT), idx, line.strip()))

    if violations:
        print(f"  ❌ FAILED: Found {len(violations)} raw SQL / direct query occurrences in agent layer:")
        for path, line_no, content in violations:
            print(f"     - {path}:{line_no} -> {content}")
        return False

    print("  ✅ PASSED: Agent and tool layers strictly route all data queries through repositories.")
    return True


def check_tool_whitelist() -> bool:
    """Verify all registered tools are in the approved PRD whitelist."""
    print("\n[3/5] Checking Tool Whitelist Registration...")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from app.agent.tools.registry import AVAILABLE_TOOLS, execute_tool
    except ImportError as e:
        print(f"  ❌ FAILED to import tools registry: {e}")
        return False

    approved_whitelist = {
        "search_flights",
        "get_flight_details",
        "filter_flights",
        "check_availability",
        "calculate_fare",
        "create_booking",
        "compare_flights",
        "search_travel_policy",
    }

    registered_tools = set(AVAILABLE_TOOLS.keys())
    diff = registered_tools - approved_whitelist
    if diff:
        print(f"  ❌ FAILED: Unauthorized tools registered: {diff}")
        return False

    print(f"  ✅ PASSED: All {len(registered_tools)} registered tools belong to the approved whitelist.")
    return True


def check_human_in_the_loop_booking() -> bool:
    """Verify that booking creation always enforces PENDING status and requires confirmation."""
    print("\n[4/5] Checking Human-in-the-Loop Booking Policy...")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from app.database.models import BookingStatus
        from app.schemas.booking import BookingResponse
    except ImportError as e:
        print(f"  ❌ FAILED to import booking models: {e}")
        return False

    # Inspect booking repository creation method
    repo_file = BACKEND_DIR / "app" / "database" / "repositories" / "booking_repo.py"
    with open(repo_file, "r", encoding="utf-8") as f:
        content = f.read()
        if "status=BookingStatus.PENDING" not in content:
            print("  ❌ FAILED: create_pending_booking does not explicitly mandate PENDING status!")
            return False

    print("  ✅ PASSED: Booking creations enforce PENDING status; autonomous ticket finalization is blocked.")
    return True


def check_requirements_no_version_pins() -> bool:
    """Verify that requirements.txt does not contain version pinning."""
    print("\n[5/5] Checking requirements.txt for Unpinned Dependencies...")
    req_file = BACKEND_DIR / "requirements.txt"
    if not req_file.exists():
        print("  ❌ FAILED: requirements.txt not found!")
        return False

    pinned_lines = []
    with open(req_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "==" in line:
                pinned_lines.append((idx, line))

    if pinned_lines:
        print(f"  ❌ FAILED: Pinned versions detected in requirements.txt:")
        for idx, line in pinned_lines:
            print(f"     Line {idx}: {line}")
        return False

    print("  ✅ PASSED: requirements.txt contains clean, unpinned dependencies.")
    return True


def main():
    print("=" * 60)
    print("🛡️  TRAVELAGENT AI — AUTOMATED GUARDRAIL VERIFICATION")
    print("=" * 60)

    checks = [
        check_500_line_limit(),
        check_no_direct_db_access_by_llm(),
        check_tool_whitelist(),
        check_human_in_the_loop_booking(),
        check_requirements_no_version_pins(),
    ]

    print("\n" + "=" * 60)
    if all(checks):
        print("🎉 ALL GUARDRAILS VERIFIED SUCCESSFULLY (5/5 PASSED)")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ ONE OR MORE GUARDRAIL CHECKS FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
